import pygame
import pygame.camera

def camPicture():
    pygame.camera.init()
    pygame.camera.list_cameras() #Camera detected or not
    cam = pygame.camera.Camera("/dev/video0",(1280,1024))
    cam.start()
    img = cam.get_image()
    pygame.image.save(img,"filename.jpg")
    cam.stop()
    

camPicture()
camPicture()
camPicture()
camPicture()
