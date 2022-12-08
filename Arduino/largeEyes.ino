#include "LedControl.h"
#include <Servo.h>
#include <string.h>

LedControl lc = LedControl(11, 13, 10, 2); // Pins: DIN,CLK,CS, # of Display connected
Servo servo_microphone, servo_mouth1, servo_mouth2, servo_foot;

// Put values in arrays
byte eyeOff[] =
{
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000
};

byte eyeOpened[] =
{
  B00000000,
  B01111110,
  B10000001,
  B10110001,
  B10110001,
  B10000001,
  B01111110,
  B00000000

};

byte eye2Closed[] =
{
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B00000000,
  B01111110,
  B00111100,
  B00000000,
};

byte eyeClosed[] =
{
  B00000000,
  B00100000,
  B01100000,
  B01100000,
  B01100000,
  B01100000,
  B00100000,
  B00000000
};

byte eye1Angry[] =
{
  B00000000,
  B01111111,
  B10000010,
  B10110100,
  B10101000,
  B10010000,
  B01100000,
  B00000000
};

byte eye2Angry[] =
{
  B00000000,
  B01100000,
  B10010000,
  B10101000,
  B10110100,
  B10000010,
  B01111111,
  B00000000
};

byte eye1Evil[] =
{
  B00000000,
  B00111100,
  B01000010,
  B10110001,
  B10110010,
  B01000100,
  B00111000,
  B00000000
};

byte eye2Evil[] =
{
  B00000000,
  B00111000,
  B01000100,
  B10110010,
  B10110001,
  B01000010,
  B00111100,
  B00000000
};

void setup()
{
  Serial.begin(9600);
  Serial.setTimeout(10);

  servo_microphone.attach(3);
  servo_mouth1.attach(5);
  servo_mouth2.attach(6);
  servo_foot.attach(9);

  servo_microphone.write(90);
  servo_mouth1.write(90);
  servo_mouth2.write(90);
  servo_foot.write(90);

  lc.shutdown(0, false); // Wake up displays
  lc.shutdown(1, false);
  lc.setIntensity(0, 1); // Set intensity levels
  lc.setIntensity(1, 1);
  lc.clearDisplay(0);  // Clear Displays
  lc.clearDisplay(1);
}

void SetLeftEye(byte* mood)
{
  for (int i = 0; i < 8; i++)
  {
    lc.setRow(1, i, mood[i]);
  }
}

void SetEye(byte* mood)
{
  for (int i = 0; i < 8; i++)
  {
    lc.setRow(1, i, mood[i]);
  }
}

void SetRightEye(byte* mood)
{
  for (int i = 0; i < 8; i++)
  {
    lc.setRow(0, i, mood[i]);
  }
}

void loop()
{
  if (Serial.available() > 0)  {

    String text = Serial.readString();
    text.trim();

    if (text.startsWith("voice")) { //ex: voice1, voice2
      servo_microphone.write(135);

      String voice_power = text.substring(text.length() - 1);
      int power = voice_power.toInt();
      int power1 = 90 + (power * 4);
      int power2 = 90 - (power * 4);

      servo_mouth1.write(power1);
      servo_mouth2.write(power2);

      // delay(200);

      if (power > 0) {
        SetRightEye(eye1Angry);
        SetLeftEye(eye2Angry);
      }
      
    } else if (text == "no-voice") {

      servo_microphone.write(90);
      servo_mouth1.write(90);
      servo_mouth2.write(90);
      // delay(200);

      SetRightEye(eyeOpened);
      SetLeftEye(eyeOpened);
    }

    if (text.startsWith("beat")) {

      String beat = text.substring(4, text.length());
      int index = beat.toInt() % 2;
      if ( index > 0 ) {
        servo_foot.write(77);
      } else {
        servo_foot.write(103);
      }
    }
  }
}


//  SetRightEye(eyeOpened);
//  SetLeftEye(eyeOpened);
//  delay(2000);
//
//  SetRightEye(eyeClosed);
//  SetLeftEye(eyeClosed);
//  delay(2000);
//
//  SetRightEye(eye1Angry);
//  SetLeftEye(eye2Angry);
//  delay(2000);
//
//  SetRightEye(eye1Evil);
//  SetLeftEye(eye2Evil);
//  delay(2000);
