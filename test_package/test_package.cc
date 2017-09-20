#include <stdio.h>
#include <libusb-1.0/libusb.h>

int main()
{
	libusb_context *ctx;
	int ret = libusb_init(&ctx);
	if (ret)
	{
		printf("Couldn't initialize libusb.\n");
		return -1;
	}

	libusb_device **list;
	ssize_t count = libusb_get_device_list(ctx, &list);
	printf("Successfully initialized libusb.  Detected %ld currently-attached devices.\n", count);

	libusb_free_device_list(list, 1);
	libusb_exit(ctx);

	return 0;
}
