import boto3 
from botocore.exceptions import NoCredentialsError
from decouple import config

# initialize s3 client 

print(config('AWS_ACCESS_KEY_ID'))
s3 = boto3.client(
    's3',
    aws_access_key_id=config('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY"),
    region_name=config("AWS_S3_REGION_NAME"),

)

def upload_image_to_s3(image_file,image_name):
    print('se utils called')
    try:
        content_type=getattr(image_file,'content_type','image/jpeg')
        # encode image name into url
        encoded_image_name=image_name

    
        print(f'Uploading :{image_name} to S3...')
        s3.upload_fileobj(
             image_file,
             config("AWS_STORAGE_BUCKET_NAME"),
             encoded_image_name,
             ExtraArgs={'ContentType':content_type},

        )
        

        return f"https://{config('AWS_STORAGE_BUCKET_NAME')}.s3.{config('AWS_S3_REGION_NAME')}.amazonaws.com/{image_name}"
        
    except NoCredentialsError:
        print('No Aws Credentials found')
        return  None
    except Exception as e :
        print(f's3 upload error : {e}')
        return None

