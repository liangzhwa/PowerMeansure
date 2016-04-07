#include     <stdio.h>      
#include     <stdlib.h>     
#include     <string.h>     
#include     <unistd.h>     
#include     <sys/types.h>  
#include     <sys/stat.h>   
#include     <fcntl.h>      
#include     <termios.h>    /*PPSIX terminal control definition*/
#include     <errno.h>      /*the def of error number*/
#include     <time.h>

#define TRUE 1
#define FALSE 0

unsigned short crc_ta[16]={ 
    0x0000,0x1021,0x2042,0x3063,0x4084,0x50a5,0x60c6,0x70e7,  
    0x8108,0x9129,0xa14a,0xb16b,0xc18c,0xd1ad,0xe1ce,0xf1ef  
};

unsigned short genCRC16(unsigned char *ptr,  unsigned int len)  
{  
    unsigned short crc = 0x0000;
    unsigned char da;

    while(len--!=0) {  
        da = ((unsigned char)(crc/256))/16;         
        crc<<=4;                                    
        crc^=crc_ta[da^(*ptr/16)];                  
        da = ((unsigned char)(crc/256))/16;         
        crc<<=4;                                    
        crc^=crc_ta[da^(*ptr&0x0f)];                
        ptr++;  
    }
    
    //printf("crc = %x\n", crc&0x0000ffff);

    return crc;
}

void set_speed(int fd, int speed)
{
    //int   i;
    int   status;
    struct termios   Opt;
    tcgetattr(fd, &Opt);
    cfsetispeed(&Opt, B38400);
    cfsetospeed(&Opt, B38400);
    tcflush(fd, TCIOFLUSH);
    status = tcsetattr(fd, TCSANOW, &Opt);
    if  (status != 0)
        perror("tcsetattr fd1");
}

int set_Parity(int fd,int databits,int stopbits,int parity)
{
	struct termios options;
	if  ( tcgetattr( fd,&options)  !=  0)
	{
  		perror("SetupSerial 1");
  		return(FALSE);
	}
	options.c_cflag &= ~CSIZE;
	switch (databits) /*set DATA bit*/
	{
  		case 7:
  			options.c_cflag |= CS7;
  			break;
  		case 8:
			options.c_cflag |= CS8;
			break;
		default:
			fprintf(stderr,"Unsupported data size\n");
		return (FALSE);
	}
	switch (parity)
  	{
  		case 'n':
		case 'N':
			options.c_cflag &= ~PARENB;		/* Clear parity enable */
			options.c_iflag &= ~INPCK;		/* Enable parity checking */
			break;
		case 'o':
		case 'O':
			options.c_cflag |= (PARODD | PARENB);  /* set as ODD parity*/ 
			options.c_iflag |= INPCK;				/* Disnable parity checking */
			break;
		case 'e':
		case 'E':
			options.c_cflag |= PARENB;		/* Enable parity */
			options.c_cflag &= ~PARODD;		/* set as EVEN parity*/  
			options.c_iflag |= INPCK;       /* Disnable parity checking */
			break;
		case 'S':
		case 's':  /*as no parity*/
			options.c_cflag &= ~PARENB;
			options.c_cflag &= ~CSTOPB;
			break;
		default:
			fprintf(stderr,"Unsupported parity\n");
			return (FALSE);
	}
	/* set STOP bit*/   
	switch (stopbits)
	{
	case 1:
		options.c_cflag &= ~CSTOPB;  /* two STOP bits */
		break;
	case 2:
		options.c_cflag |= CSTOPB;
		break;
	default:
		fprintf(stderr,"Unsupported stop bits\n");
		return (FALSE);
	}
	/* Set input parity option */
	if (parity != 'n') {
		options.c_iflag |= INPCK;
    }
	options.c_cc[VTIME] = 150; // 15 seconds
	options.c_cc[VMIN] = 0;

	tcflush(fd,TCIFLUSH); /* Update the options and do it NOW */
	if (tcsetattr(fd,TCSANOW,&options) != 0) {
		perror("SetupSerial 3");
		return (FALSE);
	}
	return (TRUE);
}

int openDev(char *Dev)
{
	int	fd = open( Dev, O_RDWR);         //| O_NOCTTY | O_NDELAY
	if (-1 == fd) {
		perror("Can't Open Serial Port");
		return -1;
	}
	else {
		return fd;
    }

}

void receiveData(int fd, float R, float V);

int main(int argc, char **argv)
{
	int fd = 0;
	int res = 0;
    unsigned char data[32];
    float R = 0;
    float V = 0;
    unsigned short crc = 0x0000;
    if (argc == 4)
    {
        R = atof(argv[2]);
        V = atof(argv[3]);
    }
    else 
    {
        printf("Usage: rs ttyNAME Resistance Voltage\n");    
        return -1;
    }
	char *dev = argv[1];

	fd = openDev(dev);
	if (fd>0)
		set_speed(fd,38400);
	else
	{
		printf("Can't Open Serial Port!\n");
		exit(0);
	}
	if (set_Parity(fd,8,1,'N')== FALSE)
	{
		printf("Set Parity Error\n");
		exit(1);
	}

    data[0] = 0xa5;
    data[1] = 0x5a;
    data[2] = 0xfa;
    data[3] = 0xfb;
    data[4] = 0x27;
    data[5] = 0x80;
    data[6] = 0x0;
    data[7] = 0xe0;
    data[8] = 0x64;                                                                                                                                             
    genCRC16(data+2, 5);
    res = write(fd, data, 9);
    receiveData(fd, R, V);


    data[2] = 0xf4;                                                                                                                                                   
    data[3] = 0xfb;
    data[4] = 0x26;
    data[5] = 0x80;
    data[6] = 0x01;
    data[7] = 0x00;
    crc = genCRC16(data+2, 6);
    data[8] = (crc>>8) & 0x000000ff;
    data[9] = crc & 0x000000ff;
    res = write(fd, data, 10);
    receiveData(fd, R,V);

    // Set V ouput
    //printf("double V = %f\n", V*100);
    int intV = V*100;
    //printf("the intV: %d\n", intV);
    //printf("the intV: %x\n", intV);
    data[4] = 0x20;
    data[5] = 0x80;
    data[6] = 0x02;
    data[7] = (intV >> 8) & 0xff;
    //printf("data[7]: %x\n", data[7]);
    data[8] = intV  & 0xff;
    //printf("data[8]: %x\n", data[8]);
    crc = genCRC16(data+2, 7);
    data[9] = (crc>>8) & 0x000000ff;
    data[10] = crc & 0x000000ff;
    res = write(fd, data, 11);
    receiveData(fd, R, V);

    // Set OV
    data[4] = 0x22;
    data[5] = 0x80;
    data[6] = 0x02;
    data[7] = 0x0c;
    data[8] = 0xb2;
    crc = genCRC16(data+2, 7);
    data[9] = (crc>>8) & 0x000000ff;
    data[10] = crc & 0x000000ff;
    res = write(fd, data, 11);
    receiveData(fd, R, V);

    // Set OI
    data[4] = 0x23;
    data[5] = 0x80;
    data[6] = 0x02;
    data[7] = 0x0c;
    data[8] = 0x1c;
    crc = genCRC16(data+2, 7);
    data[9] = (crc>>8) & 0x000000ff;
    data[10] = crc & 0x000000ff;
    res = write(fd, data, 11);
    receiveData(fd, R, V);

    data[4] = 0x24;
    data[5] = 0x80;
    data[6] = 0x01;
    data[7] = 0x01;
    crc = genCRC16(data+2, 6);
    data[8] = (crc>>8) & 0x000000ff;
    data[9] = crc & 0x000000ff;
    res = write(fd, data, 10);
    receiveData(fd, R, V);

    while (1) {
    data[4] = 0x28;
    data[5] = 0x80;
    data[6] = 0x00;
    crc = genCRC16(data+2, 5);
    data[7] = (crc>>8) & 0x000000ff;
    data[8] = crc & 0x000000ff;
    res = write(fd, data, 9);
    receiveData(fd, R, V);

    }

	close(fd);
}

void receiveData(int fd, float R, float V)
{
    //int i =0;
    int bufLen = 0;
    int cmdRead = 0;
    unsigned char buf[32];
    unsigned char cmd[32];

    //int dataV = V*100;
    int dataI = 0;
    float avgI = 0;

    static long long sumI = 0;
    static long count = 0;
	
    // receive one cmd
    while(1) {
	    bufLen = read(fd,buf,32); 

        if(0xa5==(buf[0]&0x000000ff) && 0x5a==(buf[1]&0x000000ff)) {  // Start a new cmd
            memcpy(cmd, buf, bufLen);
            cmdRead = bufLen;
        } else {    // append cmd
            memcpy(cmd+cmdRead, buf, bufLen);
            cmdRead += bufLen;
        }
            
        if (cmdRead>=7) {
            if (cmdRead == (7+(int)(cmd[6])+2)) {
                break;
            }
        }
            
    }
/*	
    printf("[Info]: received one cmd - [ ");
    for(i=0; i<cmdRead; i++) {
	    printf("%x ", cmd[i]&0x000000ff);
    }
    printf("]\n");
*/
    if (0x28==(cmd[4]&0x000000ff)) {
        //dataV = ((cmd[8]&0x000000ff) << 8) | (cmd[9]&0x000000ff);
        dataI = ((cmd[10]&0x000000ff) << 8) | (cmd[11]&0x000000ff);
	    //printf("[Info]: (V, I) - (%.2f,%.3f)\n", (float)dataV/100, (float)dataI/1000);
        sumI += dataI;
        count ++;
        if (count  == 500) {
            avgI = (float)sumI/count/1000;
            //printf("[Current]:>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   %.4f\n", avgI);
            //printf("[line power]:>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   %.4f\n", avgI*R*avgI);
            //printf("[Avg Power]: %.3f\n", ((float)dataV/100 - avgI*R)*avgI);
            //printf("[V]:>>>>>>>>>>>>>>>>>>>>>>>>>>>>  %.4f\n", V);
            //printf("[total power]:>>>>>>>>>>>>>>>>>>>>> %.4f\n", V*avgI);
            printf("[Avg Power]: %.4f\n", (V - avgI*R)*avgI);
            count = 0;
            sumI  = 0;
            avgI = 0;
        }
    }
}
