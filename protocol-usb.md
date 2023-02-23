# UBOOT's USB protocol

A chip under UBOOT mode, is visible on USB as an ordinary mass storage device,
and so it uses custom SCSI commands to do various stuff.

## MaskROM commands

Commands that are available in the MaskROM stage, i.e. in the UBOOT1.00 variant.

### Write memory

- Command: `FB 06 AA:aa:aa:aa SS:ss -- cc:CC`
  * AA:aa:aa:aa = Memory address
  * SS:ss = Size of data
  * cc:CC = CRC16 of data
- Data in: data to be written

**Note:** Some chips accept the data encrypted!

### Read memory

- Command: `FD 07 AA:aa:aa:aa SS:ss`
  * AA:aa:aa:aa = Memory address
  * SS:ss = Size of data
- Data out: data that was read

**Note:** Some chips return the data encrypted!

### Jump to memory

- Command: `FB 08 AA:aa:aa:aa BB:bb`
  * AA:aa:aa:aa = Memory address
  * BB:bb = Argument

The code is called with a pointer to the "arglist" stored in register R0,
whose structure is that:
```c
struct JieLi_LoaderArgs {
	void (*msd_send)(void *ptr, int len);		// send data
	void (*msd_recv)(void *ptr, int len);		// receive data
	int (**msd_hook)(struct usb_msc_cbw *cbw);	// SCSI command hook
	uint32_t arg;		// a passed argument
	uint32_t wtw_10;	// ? toggles on BR17, always zero on BR25..
};
```

The response to this command is sent after the code returns, and if the SCSI command hook was set,
then it will be called on *all* SCSI commands received.

If the hook returns zero then the command will be handled by the MaskROM/etc.

The hook gets reset when this command is executed.

## Loader commands (BR17/BR21/etc)

Commands that supplement the MaskROM command set; available from the Loader or the UBOOT2.00 variant.

### Erase flash block (64k)

- Command: `FB 00 AA:aa:aa:aa`
  * AA:aa:aa:aa = Address of the block
- Data out: `FB 00 -- -- -- -- -- -- -- -- -- -- -- -- -- --`

### Erase flash sector (4k)

- Command: `FB 01 AA:aa:aa:aa`
  * AA:aa:aa:aa = Address of the sector
- Data out: `FB 01 -- -- -- -- -- -- -- -- -- -- -- -- -- --`

### Erase flash chip

- Command: `FB 02 -- -- -- --`
- Data out: `FB 02 -- -- -- -- -- -- -- -- -- -- -- -- -- --`

*Note:* seems to be not always present..

### Write flash

- Command: `FB 04 AA:aa:aa:aa SS:ss`
  * AA:aa:aa:aa = Address
  * SS:ss = Size of data
- Data in: data to be written

### Read flash

- Command: `FD 05 AA:aa:aa:aa SS:ss`
  * AA:aa:aa:aa = Address
  * SS:ss = Size of data
- Data out: data that was read

### Get chipkey

- Command: `FC 09 AA:aa:aa:aa`
  * AA:aa:aa:aa = magic value, for AC69xx it's 0xAC6900
- Data out: `FC 09 -- -- -- -- KK:kk -- -- -- -- -- -- -- --`
  * KK:kk = Chipkey (little-endian value gets encrypted then put there in big-endian...)

### Get online device

- Command: `FC 0A -- -- -- --`
- Data out: `FC 0A AA -- bb:bb:bb:BB -- -- -- -- -- -- -- --`
  * AA = Device type:
    * 0 - no device
    * 1 - SDRAM
    * 2 - SD card
    * 3 - SPI0 NOR flash
    * 4 - SPI0 NAND flash
    * 16 = SD card
    * 17 = SD card
    * 18 = SD card
    * 19 = ?
    * 20 = ?
    * 21 = ?
    * 22 = SPI1 NOR flash
    * 23 = SPI1 NAND flash
  * bb:bb:bb:BB = Device ID (for SPI flash it's the JEDEC ID returned with command 0x9F)

### Reset

- Command: `FC 0C AA:aa:aa:aa`
  * AA:aa:aa:aa = reset code? set to 1..
- Data out: `FC 0C -- -- -- -- -- -- -- -- -- -- -- -- -- --`

### Burn chipkey

- Command: .....

### Get flash CRC16

- Command: `FC 13 AA:aa:aa:aa SS:ss`
  * AA:aa:aa:aa = Address
  * SS:ss = Size
- Data out: `FC 13 CC:cc -- -- -- -- -- -- -- -- -- -- -- --`
  * CC:cc = Calculated CRC16

### Get max flash page size

- Command: `FC 14 -- -- -- --`
- Data out: `FC 14 SS:ss:ss:ss -- -- -- -- -- -- -- -- -- --`
  * SS:ss:ss:ss = Page size (or maximum amount of data that can be read/written at once)