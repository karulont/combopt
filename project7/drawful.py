from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import project7

COL_RANGE = 16 ** 6  # as hex and RRGGBB


def draw(pointSnapshots):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    delta = COL_RANGE // len(pointSnapshots[0])  # how much every line can increase in color
    curr_color = 0
    for p_i in range(len(pointSnapshots[0])):
        X = []
        Y = []
        Z = []
        for snapshot_i in range(len(pointSnapshots)):
            x, y, z = pointSnapshots[snapshot_i][p_i]
            X += [x]
            Y += [y]
            Z += [z]
        color_as_hex = '#' + hex(curr_color)[2:].zfill(6)
        ax.plot(X, Y, Z, color=color_as_hex, linestyle='-', linewidth=2, marker='*')
        curr_color += delta

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()


if __name__ == '__main__':
    fn = 'points-00100-0.lst'
    # fn = 'example-points.lst'
    pointSnaps = project7.read_instance_from_file(fn)
    print("pointSnaps:", len(pointSnaps))
    draw(pointSnaps)


