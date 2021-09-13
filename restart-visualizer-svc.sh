
# Sample:
# bash restart-visualizer-svc.sh 2
# Destroying and re-deploying 2 visualizer services

# Capturing expected total number of worker nodes (input arguments)
NUMDRONE=$1
VERSION=$2

## check number of connected drones
if [ -z "$NUMDRONE" ]
then
      echo "\$$NUMDRONE is empty"
      NUMDRONE=1  # default value
else
      echo "\$$NUMDRONE is NOT empty (=${NUMDRONE})"
fi

## check version
if [ -z "$VERSION" ]
then
      echo "\$VERSION is empty"
      VERSION="2.4"  # default value
else
      echo "\$VERSION is NOT empty (=${VERSION})"
fi

# Deleting Visualizer Services
echo "Deleting all visualizer-service; Total=${NUMDRONE}..."
for i in $(seq 1 $NUMDRONE);
  do
    docker container rm -f "viz-rtsp-ee-svc-${i}";
    docker container rm -f "viz-rtsp-raw-svc-${i}";
done

# Deploying Visualizer Services
echo "Deploying Visualizer Services ..."
for i in $(seq 1 $NUMDRONE);
  do
    docker run --name "viz-rtsp-ee-svc-${i}" -d \
                  --network host \
                  -v "/home/s010132/devel/eagleeye/visualizer-service/etc/site-rtsp-${i}.conf:/app/etc/site.conf" \
                  "5g-dive/eagleeye/visualizer-service:${VERSION}"
    echo "[viz-rtsp-ee-svc-${i}] is deployed ..."

    docker run --name "viz-rtsp-raw-svc-${i}" -d \
                  --network host \
                  -v "/home/s010132/devel/eagleeye/visualizer-service/etc/site-rtsp-raw-${i}.conf:/app/etc/site.conf" \
                  "5g-dive/eagleeye/visualizer-service:${VERSION}"
    echo "[viz-rtsp-raw-svc-${i}] is deployed ..."

done

echo ""
echo "Restarting Visualizer services finished. Enjoy! :)"