String name, toptext, bottomtext;

PGraphics img;

int h = 100;

void setup() {
  surface.initOffscreen(this);
  
  name = args[0];
  toptext = args[1].replace('~', ' ');
  bottomtext = args[2].replace('~', ' ');
  h = int(args[3]);
  
  println(toptext, bottomtext);
  
  img = createGraphics(1280, 312 + h);
  img.beginDraw();
  img.background(0);
  img.fill(0);
  img.stroke(0);
  img.rect(0, img.height - 200, img.width, 200);
  PFont font = createFont("Times New Roman", 128);
  img.textAlign(CENTER, CENTER);
  img.stroke(255);
  img.fill(255);
  img.textFont(font, 100);
  img.text(toptext, img.width / 2, img.height - 180);
  img.textFont(font, 40);
  img.text(bottomtext, img.width / 2, img.height - 70);
  img.rectMode(CORNERS);
  img.fill(0);
  img.strokeWeight(5);
  img.rect(94, 71, img.width - 95, img.height - 240);
  img.endDraw();
  img.save(name);
  exit();
}
