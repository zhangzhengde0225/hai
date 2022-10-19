import argparse
import damei as dm


def get_args():
    parser = dm.argparse.ArgumentParser(description='Predict masks from input images')
    
    # train args
    parser.add_argument('-s', '--source', type=str, 
                            default='~/datasets/hai_datasets/carvana', 
                            help='source path of images and masks')
    parser.add_argument('--epochs', '-e', metavar='E', type=int, default=5, help='Number of epochs')
    parser.add_argument('--batch-size', '-b', dest='batch_size', metavar='B', type=int, default=4, help='Batch size')
    parser.add_argument('--learning-rate', '-l', metavar='LR', type=float, default=1e-5,
                        help='Learning rate', dest='lr')
    parser.add_argument('--weights', '-w', type=str, default=None, help='trained model weights path')
    parser.add_argument('--scale', type=float, default=0.5, help='Downscaling factor of the images')
    parser.add_argument('--validation', '-v', dest='val', type=float, default=10.0,
                        help='Percent of the data that is used as validation (0-100)')
    parser.add_argument('--amp', action='store_true', default=False, help='Use mixed precision')
    parser.add_argument('--bilinear', action='store_true', default=False, help='Use bilinear upsampling')
    parser.add_argument('--classes', '-c', type=int, default=2, help='Number of classes')
    parser.add_argument('--lr', type=float, default=1e-5, help='learning rate')
    # parser.add_argument('--val', type=float, default=10.0, help='validation percent')
    # infer args

    # parser.add_argument('--model', '-m', default='MODEL.pth', metavar='FILE',
    #                     help='Specify the file in which the model is stored')
    # parser.add_argument('--input', '-i', metavar='INPUT', nargs='+', help='Filenames of input images', required=True)
    parser.add_argument('--output', '-o', default='runs/outputs', help='Filenames of output images')
    parser.add_argument('--viz', action='store_true',
                        help='Visualize the images as they are processed')
    parser.add_argument('--no-save', '-n', action='store_true', help='Do not save the output masks')
    parser.add_argument('--mask-threshold', '-t', type=float, default=0.5,
                        help='Minimum probability value to consider a mask pixel white')
    
    parser.add_argument('--device', '-d', default='cuda', help='Device to use for inference')

    return parser.parse_args()