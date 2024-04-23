import json
import os
import boto3
import uuid 
from datetime import datetime

from boto3.dynamodb.conditions import Key

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ADVERTS_TABLE_NAME'])

def getAllAdverts(event, context):
    # Scan the table to fetch all adverts
    try:
        result = table.scan()
        items = result.get('Items', [])
        response = {
            "statusCode": 200,
            "headers": {
                        "Content-Type": "application/json",
                        "Cache-Control": "no-cache"  # Ensures fresh data for listing adverts
            },
            "body": json.dumps({"adverts": items})
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": str(e)})
        }
    return response


def getAdvertDetails(event, context):
    # Extract the advert ID from the path parameters
    advert_id = event['pathParameters']['id']
    try:
        # Fetch the advert details from DynamoDB using the advert_id
        result = table.get_item(Key={'id': advert_id})
        item = result.get('Item', None)
        if item:
            response = {
                "statusCode": 200,
                "headers": {
                        "Content-Type": "application/json",
                        "Cache-Control": "no-cache"  # Ensures fresh data for listing adverts
            },
                "body": json.dumps(item)
            }
        else:
            response = {
                "statusCode": 404,
                "headers": {
                "Content-Type": "application/json",
            },
                "body": json.dumps({"message": "Advert not found"})
            }
    except Exception as e:
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": str(e)})
        }
    return response

def postAdvert(event, context):
    # Generate a unique UUID for the new advert
    advert_id = str(uuid.uuid4())

    # Parse the request body to create a new advert
    advert_details = json.loads(event['body'])
    advert_details['id'] = advert_id

    # Extract the user email from the Cognito context (provided by API Gateway)
    try:
        user_email = event['requestContext']['authorizer']['claims']['email']
    except KeyError:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": "User email not found in the request context"})
        }

    # Add user email to the advert details
    advert_details['userEmail'] = user_email

    try:
        # Insert advert details into DynamoDB
        table.put_item(Item=advert_details)
        response = {
            "statusCode": 201,
            "headers": {
                        "Content-Type": "application/json",
                        "Cache-Control": "no-cache"  # Ensures fresh data for listing adverts
            },
            "body": json.dumps({
                "message": "Advert created successfully",
                "advertId": advert_id,
                "advertDetails": advert_details
            })
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": str(e)})
        }

    return response

def getUserAdverts(event, context):
    try:
        # Extract the user email from the Cognito claims in the request context
        user_email = event['requestContext']['authorizer']['claims']['email']
        # Query DynamoDB using the GSI for the user email
        result = table.query(
            IndexName='UserEmailIndex',
            KeyConditionExpression=Key('userEmail').eq(user_email)
        )
        items = result.get('Items', [])
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"  # Ensures fresh data for listing adverts
            },
            "body": json.dumps({"adverts": items})
        }
    except Exception as e:
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": json.dumps({"error": str(e)})
        }
    return response


# COMMENTS / CHAT

commmentstable = dynamodb.Table(os.environ['COMMENTS_TABLE_NAME'])

def postAdvertComment(event, context):
    try:
        # Extract data from the request body
        body = json.loads(event['body'])
        advert_id = body['advertId']
        user_email = body['userEmail']
        comment_text = body['commentText']
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Generate a unique comment ID
        comment_id = f"{advert_id}-{timestamp}"
        
        # Prepare the item to be put into DynamoDB
        item = {
            'commentId': comment_id,
            'advertId': advert_id,
            'userEmail': user_email,
            'commentText': comment_text,
            'timestamp': timestamp
        }
        
        # Put the item into DynamoDB
        commmentstable.put_item(Item=item)
        
        # Return a success response
        return {
            'statusCode': 200,
            "headers": {
                        "Content-Type": "application/json",
                        "Cache-Control": "no-cache"  # Ensures fresh data for listing adverts
            },

            'body': json.dumps({'message': 'Comment posted successfully'})
        }
    except Exception as e:
        # Return an error response if any exception occurs
        return {
            'statusCode': 500,
            "headers": {
                "Content-Type": "application/json",
            },
            'body': json.dumps({'error': str(e)})
        }
    
def getAdvertComments(event, context):
    try:
        # Extract advert ID from the request path parameters
        advert_id = event['pathParameters']['id']
        
        # Query comments associated with the advert ID
        response = commmentstable.query(
            KeyConditionExpression='advertId = :advert_id',
            ExpressionAttributeValues={
                ':advert_id': advert_id
            }
        )
        
        # Extract comments from the response
        comments = response['Items']
        
        # Return the comments as the response
        return {
            'statusCode': 200,
            "headers": {
                        "Content-Type": "application/json",
                        "Cache-Control": "no-cache"  # Ensures fresh data for listing adverts
            },
            'body': json.dumps(comments)
        }
    except Exception as e:
        # Return an error response if any exception occurs
        return {
            'statusCode': 500,
            "headers": {
                "Content-Type": "application/json",
            },
            'body': json.dumps({'error': str(e)})
        }