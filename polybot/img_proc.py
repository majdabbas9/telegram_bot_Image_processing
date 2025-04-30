from pathlib import Path
from matplotlib.image import imread, imsave
import re

def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        if not self.path.exists():
            raise RuntimeError(f"Image path does not exist: {self.path}")

        # Check if the image is RGB
        image_data = imread(path)
        if image_data.ndim != 3 or image_data.shape[2] != 3:
            raise RuntimeError("Input image is not in RGB format.")

        self.data = rgb2gray(image_data).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=16):

        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j-1] - row[j]))

            self.data[i] = res

    def rotate(self):
        matrix = self.data
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if i > j:
                    matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        for i in range(len(matrix)):
            matrix[i] = matrix[i][::-1]
        self.data = matrix
    # def rotate(self):
    #     matrix = self.data
    #     rotated = [[matrix[row][col] for row in reversed(range(len(matrix)))] for col in range(len(matrix[0]))]
    #     self.data = rotated

    def rotate_in_steps(self,steps):
        if steps>=4 or steps<=-4:
            steps %=4

        if steps < 0:
            steps = 4 + steps

        while steps  > 0:
            self.rotate()
            steps -= 1

    def salt_n_pepper(self):
        import random
        matrix = self.data
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                number_in_01 = random.random()
                if number_in_01 < 0.2:
                    matrix[i][j] = 255
                elif number_in_01 > 0.8:
                    matrix[i][j] = 0
        self.data = matrix


    def concat(self, other_img, direction='horizontal'):
        mat1 = self.data
        mat2 = other_img.data
        if direction == 'horizontal':
            if len(mat1) != len(mat2):
                raise ValueError("Images must have the same height for horizontal concatenation.")
            result = []
            for i in range(len(mat1)):
                new_row = mat1[i]
                new_row.extend(mat2[i])
                result.append(new_row)
            self.data = result

        elif direction == 'vertical':
            if len(mat1[0]) != len(mat2[0]):
                raise ValueError("Images must have the same width for vertical concatenation.")
            result = []
            for i in range(len(mat1)):
                new_row = mat1[i]
                result.append(new_row)
            for i  in range(len(mat2)):
                new_row = mat2[i]
                result.append(new_row)
            self.data = result

    def segment(self,segment_level=100):
        matrix = self.data
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if matrix[i][j] > segment_level:
                    matrix[i][j] = 255
                else:
                    matrix[i][j] = 0
        self.data = matrix

    def check_rotate_in_filtername(self, filter_name):
        if filter_name.startswith('rotate') or filter_name.startswith('r'):
            if len(filter_name) == 6 or filter_name=='r':
                return 1
            match = re.fullmatch(r'-?\d+', filter_name[6:].replace(" ", ""))
            if match:
                return int(match.group())
            else :
                match = re.fullmatch(r'^r-?\d+$', filter_name.replace(" ", ""))
                if match:
                    return int(match.group()[1:])
                else :
                    return None
        else :
            return None



if __name__ == '__main__':
    my_img = Img('images_to_test/1.jpg')
    # my_img.rotate_in_steps(-2)
    # my_img.save_img()