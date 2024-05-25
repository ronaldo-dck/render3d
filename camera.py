import pygame as pg
from matrix_functions import *


class Camera:
    def __init__(self, position, foco, viewUP):
        self.position = np.array(position)
        self.foco = np.array(foco)
        self.viewUP = np.array(viewUP)
        self.near_plane = 0.1
        self.far_plane = 100
        self.moving_speed = 0.3
        self.rotation_speed = 0.015

        self.anglePitch = 0
        self.angleYaw = 0
        self.angleRoll = 0

    def control(self):
        key = pg.key.get_pressed()
        if key[pg.K_a]:
            self.position -= self.u * self.moving_speed
        if key[pg.K_d]:
            self.position += self.u * self.moving_speed
        if key[pg.K_w]:
            self.position += self.n * self.moving_speed
        if key[pg.K_s]:
            self.position -= self.n * self.moving_speed
        if key[pg.K_q]:
            self.position += self.v * self.moving_speed
        if key[pg.K_e]:
            self.position -= self.v * self.moving_speed

        if key[pg.K_LEFT]:
            self.camera_yaw(-self.rotation_speed)
        if key[pg.K_RIGHT]:
            self.camera_yaw(self.rotation_speed)
        if key[pg.K_UP]:
            self.camera_pitch(-self.rotation_speed)
        if key[pg.K_DOWN]:
            self.camera_pitch(self.rotation_speed)

    def camera_yaw(self, angle):
        self.angleYaw += angle

    def camera_pitch(self, angle):
        self.anglePitch += angle

    def camera_matrix(self):
        return self.rotate_matrix() @ self.translate_matrix()

    def translate_matrix(self):
        x, y, z = self.position
        return np.array([
            [1, 0, 0, -x],
            [0, 1, 0, -y],
            [0, 0, 1, -z],
            [0, 0, 0, 1]
        ])

    def rotate_matrix(self):
        Y = self.viewUP

        n = normalize(self.position - self.foco)
        v = normalize(
            Y - (np.dot(Y, n)*n)
        )
        u = np.cross(v, n)

        self.n = n
        self.u = u
        self.v = v

        return np.array([
            [u[0], u[1], u[2], 0],
            [v[0], v[1], v[2], 0],
            [n[0], n[1], n[2], 0],
            [0, 0, 0, 1]
        ])


if __name__ == '__main__':
    camera = Camera((25, 15, 80), (20, 10, 25), (0, 1, 0))
    print(np.round(camera.rotate_matrix(), 3))
    print()
    print(camera.translate_matrix())
    print()
    print(np.round(camera.camera_matrix(), 3))