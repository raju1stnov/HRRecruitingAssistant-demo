curl -X POST http://localhost:8005/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "start_recruiting_workflow",
    "params": {
      "username": "admin",
      "password": "secret",
      "title": "Data Scientist",
      "skills": "Python, Machine Learning"
    },
    "id": 1
}'