curl -v -X POST https://api.line.me/v2/bot/richmenu \
-H 'Authorization: Bearer {3VfwWxCENMv3LM8MwYdWsesaaGniPjPQ2BdAH+l52fZOXs8kLkkdYd3ECSKQbJUBqW/tjFbnZKp62IHAFvXsDEJkJAbgLAl31Sz+7YKv+2PEQHPGxFT2KSv4G6ntF0OvdYlGwtYv04LZzFZZj5dWLQdB04t89/1O/w1cDnyilFU=}' \
-H 'Content-Type: application/json' \
-d \
'{
    "size": {
      "width": 2500,
      "height": 843
    },
    "selected": false,
    "name": "PCRD_arena",
    "chatBarText": "PCRD 競技場選單",
    "areas": [
      {
        "bounds": {
          "x": 0,
          "y": 0,
          "width": 1250,
          "height": 843
        },
        "action": {
          "type": "postback",
          "data": "action=upload"
        }
      },
      {
        "bounds": {
          "x": 1250,
          "y": 0,
          "width": 1250,
          "height": 843
        },
        "action": {
          "type": "postback",
          "data": "action=search"
        }
      }
   ]
}'