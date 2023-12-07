from gridfs import GridFS, NoFile
from pymongo import MongoClient
from bson import ObjectId

# MongoDB Connection
client = MongoClient("mongodb+srv://Mvacc:pwd@iotproject.lkfss1w.mongodb.net/?retryWrites=true&w=majority")
db = client.your_database_name
fs = GridFS(db)

def retrieve_video_from_gridfs(file_id, output_path):
    try:
        grid_out = fs.get(file_id)
        with open(output_path, 'wb') as output_file:
            output_file.write(grid_out.read())
        print("Video retrieved successfully.")
        return True
    except NoFile:
        print("No file found with this id")
        return False

# Replace 'file_id_here' with your actual file ID and specify the output path
video_id = ObjectId('65715b564850ddae77e66c19') # Replace with the actual GridFS file ID
output_path = 'output.mp4' # Replace with the desired output path

if retrieve_video_from_gridfs(video_id, output_path):
    print("Video retrieved and saved to:", output_path)
else:
    print("Failed to retrieve the video.")

