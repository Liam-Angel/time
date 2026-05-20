#include <Servo.h>

Servo myservo;
const int m1 = 10;
const int m2 = 11;
const int ena1 = 5;
const int ena2 = 3;

int mid;
String data;

void setup() 
{
  Serial.begin(9600);
  myservo.attach(9);
  myservo.write(90);
}
void loop() {
  if (Serial.available() > 0) 
  {
   data = Serial.readStringUntil('\n');
   Serial.println(data);   
   int num = data.toInt();
   mid = map(num, 0, 640, 40, 180);
   myservo.write(mid); 

   int l2 = map(num, 640, 0, 25, 100);
   int l1 = map(num, 640, 0, 130, 45);

   digitalWrite(m1, HIGH);
   digitalWrite(m2, HIGH);

   analogWrite(ena1, l1);
   analogWrite(ena2, l2);
   
  }
}
 
