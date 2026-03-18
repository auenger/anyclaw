# HTTP Request Skill

Execute HTTP requests and return responses.

## Usage

```
http <url> [--method GET|POST|PUT|DELETE] [--headers "Key: Value"] [--data "body"]
```

## Parameters

- `url`: URL to request (required)
- `method`: HTTP method (default: GET)
- `headers`: Request headers in format "Key: Value"
- `data`: Request body data

## Examples

```bash
# GET request
http https://api.example.com/data

# POST request with JSON
http https://api.example.com/create --method POST --headers "Content-Type: application/json" --data '{"name": "test"}'
```

## Requirements

- curl command must be available
