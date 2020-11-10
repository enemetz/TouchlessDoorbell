import FCMManager as fcm

tokens = ['cNwdDC6rRSWHaa5aqqChx4:APA91bGdbZUWbMOrJqGqq3fvPmlPJ6uYWRnAx87LjL5HLHbPZUVuxd0f3o0YesB6kdCDeP-zBxTWjfFV3yWDdOJzqkkoYL6PuGIQlvMf1hFuratyFkMxDHI1u_W-Dk8NpKrKHNRSn9KH']
fcm.send("Doorbell activated!", "Someone is at the door", tokens)
