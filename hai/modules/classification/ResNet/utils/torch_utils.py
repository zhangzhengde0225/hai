import os
import torch


def select_device(device='', batch_size=None):
	# device = 'cpu' or '0' or '0,1,2,3'
	cpu_request = device.lower() == 'cpu'
	if device and not cpu_request:  # if device requested other than 'cpu'
		os.environ['CUDA_VISIBLE_DEVICES'] = device  # set environment variable
		assert torch.cuda.is_available(), 'CUDA unavailable, invalid device %s requested' % device  # check availablity

	cuda = False if cpu_request else torch.cuda.is_available()
	if cuda:
		c = 1024 ** 2  # bytes to MB
		ng = torch.cuda.device_count()
		# zzd k80
		# ng = 2
		if ng > 1 and batch_size:  # check that batch_size is compatible with device_count
			assert batch_size % ng == 0, 'batch-size %g not multiple of GPU count %g' % (batch_size, ng)
		x = [torch.cuda.get_device_properties(i) for i in range(ng)]
		s = 'Using CUDA '
		for i in range(0, ng):
			if i == 1:
				s = ' ' * len(s)
			print("%sdevice%g _CudaDeviceProperties(name='%s', total_memory=%dMB)" %
				  (s, i, x[i].name, x[i].total_memory / c))
	else:
		print('Using CPU')

	print('')  # skip a line
	return torch.device('cuda:0' if cuda else 'cpu')
