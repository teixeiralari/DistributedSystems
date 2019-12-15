echo "Creating neonat proto file"

python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. neonat.proto

OUTPUT="$(ls  neonat_pb2*)"
echo "COPYING TO SERVER AND CLIENT FOLDER"
echo "${OUTPUT}"
cp neonat_pb2* ../server/
cp neonat_pb2* ../client/
echo "Succesfully created."