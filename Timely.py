from WebSocketClient import WebSocketClient
import json

class TimelyWebSocketClient(WebSocketClient):

    def __init__(self, metric, startTime, endTime, connect_timeout=WebSocketClient.DEFAULT_CONNECT_TIMEOUT,
                 request_timeout=WebSocketClient.DEFAULT_REQUEST_TIMEOUT):

        self.metric = metric
        self.startTime = startTime
        self.endTime = endTime
        # self._on_message_callback = on_message_callback
        WebSocketClient.__init__(self, connect_timeout, request_timeout)

    def _on_message(self, msg):
        # self._on_message_callback(self, msg)

        obj = json.loads(msg)
        print(str(obj.get("timestamp")) + " -- " + str(self.endTime))

        timestamp = int(obj.get("timestamp"));

        if (timestamp >= self.endTime or (self.endTime - timestamp) < 60000):
            print("exiting")
            self._on_connection_close()

    def _on_connection_success(self):
        print('Connected!')

        create = {
            "operation": "create",
            "subscriptionId": "12345",
        }
        self.send(create)

        m1 = {
            "operation": "add",
            "subscriptionId": "12345",
            "metric": self.metric,
            "startTime": self.startTime,
            "endTime" : self.endTime
        }
        self.send(m1)

    def _on_connection_close(self):
        print('Connection closed!')
        exit()

    def _on_connection_error(self, exception):
        print('Connection error: %s', exception)



