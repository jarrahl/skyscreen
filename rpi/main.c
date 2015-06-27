#include <bitthunder.h>

int main() {
	#define LED_GPIO_ID 16                                // This is for the pi model B
	BT_GpioSetDirection(LED_GPIO_ID, BT_GPIO_DIR_OUTPUT); // Set the pin to be output
	int v = 0;

	while(1) {
		//BT_kPrint("Welcome to BitThunder");         // I don't care about UART
		BT_ThreadSleep(250);                          // Wait a quarter second
		BT_GpioSet(LED_GPIO_ID, v);                   // Set the output high or low
		v = !v;                                       // and flip the output variable
	}
}
