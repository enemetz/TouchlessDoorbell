import FCMManager as fcm

tokens = ['f1xc0AfZSVGLvCIo6kJou5:APA91bEVK1inPis7jLuGHBO0akN3QDpn23_I9skNa7-o6eyHnwle3G0rvNh1ofHJ2MfXHVhPVN9_J8a8HJprCtVWZ0hX8LY11ndtrtOsXkmCCD0NE69y3-Mj5W0172S3yspLchwKmp_J']
fcm.send("Doorbell activated!", "Someone is at the door", tokens)
