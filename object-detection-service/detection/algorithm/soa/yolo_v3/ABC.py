from detection.algorithm.soa.yolo_v3.components.models import *  # set ONNX_EXPORT in models.py
from detection.algorithm.soa.yolo_v3.components.utils.utils import *


class ABC:
    def __init__(self, conf):
        self.conf = conf
        self.classify = False
        self.img_size = (320, 192) if ONNX_EXPORT else conf["img_size"]

        # Initialize model
        self.model = Darknet(conf["cfg"], self.img_size)

        # Initialize device configuration
        self.device = torch_utils.select_device(device='cpu' if ONNX_EXPORT else conf["device"])

    def _load_weight(self):
        # Load weights
        attempt_download(self.conf["weights"])
        if self.conf["weights"].endswith('.pt'):  # pytorch format
            self.model.load_state_dict(torch.load(self.conf["weights"], map_location=self.device)['model'])
        else:  # darknet format
            load_darknet_weights(self.model, self.conf["weights"])

        # Fuse Conv2d + BatchNorm2d layers
        # model.fuse()

    def _second_stage_classifier(self):
        # Second-stage classifier
        if self.classify:
            self.modelc = torch_utils.load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(torch.load('weights/resnet101.pt', map_location=self.device)['model'])  # load weights
            self.modelc.to(self.device).eval()

    def _eval_model(self):
        # Eval mode
        self.model.to(self.device).eval()

    # Optional
    def _export_mode(self):
        # Export mode
        if ONNX_EXPORT:
            img = torch.zeros((1, 3) + self.img_size)  # (1, 3, 320, 192)
            torch.onnx.export(self.model, img, 'weights/export.onnx', verbose=False, opset_version=10)

            # Validate exported model
            import onnx
            model = onnx.load('weights/export.onnx')  # Load the ONNX model
            onnx.checker.check_model(model)  # Check that the IR is well formed
            print(onnx.helper.printable_graph(model.graph))  # Print a human readable representation of the graph
            return

    def _half_precision(self):
        # Half precision
        self.half = self.half and self.device.type != 'cpu'  # half precision only supported on CUDA
        if self.half:
            self.model.half()

    # def __set_data_loader(self):
    #     # Set Dataloader
    #     self.vid_path, self.vid_writer = None, None
    #     if self.webcam:
    #         self.view_img = True
    #         self.save_img = True
    #         # self.save_img = False
    #         torch.backends.cudnn.benchmark = True  # set True to speed up constant image size inference
    #         self.dataset = LoadStreams(self.source, img_size=self.img_size, half=self.half)
    #     else:
    #         self.save_img = True
    #         self.dataset = LoadImages(self.source, img_size=self.img_size, half=self.half)

    def _get_names_colors(self):
        # Get names and colors
        self.names = load_classes(self.conf["names"])
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(self.names))]
