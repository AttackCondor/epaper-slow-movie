/*****************************************************************************
* | File      	:	EPD_7in5.c
* | Author      :   Waveshare team
* | Function    :   Electronic paper driver
* | Info        :
*----------------
* |	This version:   V2.0
* | Date        :   2018-11-09
* | Info        :
* 1.Remove:ImageBuff[EPD_HEIGHT * EPD_WIDTH / 8]
* 2.Change:EPD_Display(UBYTE *Image)
*   Need to pass parameters: pointer to cached data
* 3.Change:
*   EPD_RST -> EPD_RST_PIN
*   EPD_DC -> EPD_DC_PIN
*   EPD_CS -> EPD_CS_PIN
*   EPD_BUSY -> EPD_BUSY_PIN
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
#include "EPD_7in5.h"
#include "Debug.h"

/******************************************************************************
function :	Software reset
parameter:
******************************************************************************/
static void EPD_Reset(void)
{
    DEV_Digital_Write(EPD_RST_PIN, 1);
    DEV_Delay_ms(200);
    DEV_Digital_Write(EPD_RST_PIN, 0);
    DEV_Delay_ms(200);
    DEV_Digital_Write(EPD_RST_PIN, 1);
    DEV_Delay_ms(200);
}

/******************************************************************************
function :	send command
parameter:
     Reg : Command register
******************************************************************************/
static void EPD_SendCommand(UBYTE Reg)
{
    DEV_Digital_Write(EPD_DC_PIN, 0);
    DEV_Digital_Write(EPD_CS_PIN, 0);
    DEV_SPI_WriteByte(Reg);
    DEV_Digital_Write(EPD_CS_PIN, 1);
}

/******************************************************************************
function :	send data
parameter:
    Data : Write data
******************************************************************************/
static void EPD_SendData(UBYTE Data)
{
    DEV_Digital_Write(EPD_DC_PIN, 1);
    DEV_Digital_Write(EPD_CS_PIN, 0);
    DEV_SPI_WriteByte(Data);
    DEV_Digital_Write(EPD_CS_PIN, 1);
}

/******************************************************************************
function :	Wait until the busy_pin goes LOW
parameter:
******************************************************************************/
void EPD_WaitUntilIdle(void)
{
    Debug("e-Paper busy\r\n");
    while(DEV_Digital_Read(EPD_BUSY_PIN) == 0) {      //LOW: idle, HIGH: busy
        DEV_Delay_ms(100);
    }
    Debug("e-Paper busy release\r\n");
}


/******************************************************************************
function :	Turn On Display
parameter:
******************************************************************************/
static void EPD_TurnOnDisplay(void)
{
    EPD_SendCommand(DISPLAY_REFRESH);
    DEV_Delay_ms(100);
    EPD_WaitUntilIdle();
}

/******************************************************************************
function :	Initialize the e-Paper register
parameter:
******************************************************************************/
UBYTE EPD_Init(void)
{
    EPD_Reset();

     EPD_SendCommand(POWER_SETTING);
    EPD_SendData(0x37);
    EPD_SendData(0x00);

    EPD_SendCommand(PANEL_SETTING);
    EPD_SendData(0xCF);
    EPD_SendData(0x08);

    EPD_SendCommand(BOOSTER_SOFT_START);
    EPD_SendData(0xc7);
    EPD_SendData(0xcc);
    EPD_SendData(0x28);

    EPD_SendCommand(POWER_ON);
    EPD_WaitUntilIdle();

    EPD_SendCommand(PLL_CONTROL);
    EPD_SendData(0x3c);

    EPD_SendCommand(TEMPERATURE_CALIBRATION);
    EPD_SendData(0x00);

    EPD_SendCommand(VCOM_AND_DATA_INTERVAL_SETTING);
    EPD_SendData(0x77);

    EPD_SendCommand(TCON_SETTING);
    EPD_SendData(0x22);

    EPD_SendCommand(TCON_RESOLUTION);
    EPD_SendData(EPD_WIDTH >> 8);     //source 640
    EPD_SendData(EPD_WIDTH & 0xff);
    EPD_SendData(EPD_HEIGHT >> 8);     //gate 384
    EPD_SendData(EPD_HEIGHT & 0xff);

    EPD_SendCommand(VCM_DC_SETTING);
    EPD_SendData(0x1E);      //decide by LUT file

    EPD_SendCommand(0xe5);           //FLASH MODE
    EPD_SendData(0x03);
    
    return 0;
}

/******************************************************************************
function :	Clear screen
parameter:
******************************************************************************/
void EPD_Clear(void)
{
    UWORD Width, Height;
    Width = (EPD_WIDTH % 8 == 0)? (EPD_WIDTH / 8 ): (EPD_WIDTH / 8 + 1);
    Height = EPD_HEIGHT;

    EPD_SendCommand(DATA_START_TRANSMISSION_1);
    for (UWORD j = 0; j < Height; j++) {
        for (UWORD i = 0; i < Width; i++) {
            for(UBYTE k = 0; k < 4; k++) {
                EPD_SendData(0x33);
            }
        }
    }
    EPD_TurnOnDisplay();
}

/******************************************************************************
function :	Sends the image buffer in RAM to e-Paper and displays
parameter:
******************************************************************************/
void EPD_Display(UBYTE *Image)
{
    UBYTE Data_Black, Data;
    UWORD Width, Height;
    Width = (EPD_WIDTH % 8 == 0)? (EPD_WIDTH / 8 ): (EPD_WIDTH / 8 + 1);
    Height = EPD_HEIGHT;

    EPD_SendCommand(DATA_START_TRANSMISSION_1);
    for (UWORD j = 0; j < Height; j++) {
        for (UWORD i = 0; i < Width; i++) {
            Data_Black = ~Image[i + j * Width];
            for(UBYTE k = 0; k < 8; k++) {
                if(Data_Black & 0x80)
                    Data = 0x00;
                else
                    Data = 0x03;
                Data <<= 4;
                Data_Black <<= 1;
                k++;
                if(Data_Black & 0x80)
                    Data |= 0x00;
                else
                    Data |= 0x03;
                Data_Black <<= 1;
                EPD_SendData(Data);
            }
        }
    }
    EPD_TurnOnDisplay();
}

/******************************************************************************
function :	Enter sleep mode
parameter:
******************************************************************************/
void EPD_Sleep(void)
{
    EPD_SendCommand(POWER_OFF);
    EPD_WaitUntilIdle();
    EPD_SendCommand(DEEP_SLEEP);
    EPD_SendData(0XA5);;
}
