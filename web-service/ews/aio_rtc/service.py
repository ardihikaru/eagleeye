import asab.web
import os
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
import simplejson as json
import asyncio
import platform

pcs = set()
ROOT = os.path.dirname(__file__) + "/http_stream_files/"
# print(">> ROOT:", ROOT)


class AIORTCService(asab.Service):
    """
        AIO RTC Service
    """

    def __init__(self, app, service_name="ews.aio-rtc-service"):
        super().__init__(app, service_name)

    async def on_shutdown(self, app):
    # def on_shutdown(self, app):
        # close peer connections
        coros = [pc.close() for pc in pcs]
        await asyncio.gather(*coros)
        pcs.clear()

    async def index(self, request):
        content = open(os.path.join(ROOT, "index.html"), "r").read()
        return web.Response(content_type="text/html", text=content)

    async def javascript(self, request):
        content = open(os.path.join(ROOT, "client.js"), "r").read()
        return web.Response(content_type="application/javascript", text=content)

    async def offer(self, request):
        params = await request.json()
        offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        pc = RTCPeerConnection()
        pcs.add(pc)

        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            print("ICE connection state is %s" % pc.iceConnectionState)
            if pc.iceConnectionState == "failed":
                await pc.close()
                pcs.discard(pc)

        # open media source
        stream_id = params["data"]["stream_id"]
        if stream_id:
            # Get stream source
            stream_source = None
            player = MediaPlayer(stream_source)
        else:
            options = {
                "framerate": asab.Config["streaming:config"]["fps"],
                "video_size": "%sx%s" % (
                    asab.Config["streaming:config"]["w"],
                    asab.Config["streaming:config"]["h"]
                )
            }
            if platform.system() == "Darwin":
                player = MediaPlayer("default:none", format="avfoundation", options=options)
            else:
                player = MediaPlayer("/dev/video0", format="v4l2", options=options)
                # player = MediaPlayer("/dev/video0", format="mjpeg", options=options)
                # player = MediaPlayer("/dev/video0", format="yuyv422", options=options)

        await pc.setRemoteDescription(offer)
        for t in pc.getTransceivers():
            if t.kind == "audio" and player.audio:
                pc.addTrack(player.audio)
            elif t.kind == "video" and player.video:
                pc.addTrack(player.video)

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return web.Response(
            content_type="application/json",
            text=json.dumps(
                {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
            ),
        )
