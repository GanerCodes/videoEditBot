String name, topText, bottomText;
int width2 = 1200, height2 = 1000;

PImage crop(PImage p) {
  int xMin = p.width, xMax = 0, yMin = p.height, yMax = 0;
  for(int x = 0; x < p.width; x++) {
    for(int y = 0; y < p.height; y++) {
      color cc = p.get(x, y);
      if(cc == color(255) || cc == color(1)) {
        if(x < xMin) {
          xMin = x;
        }
        if(x > xMax) {
          xMax = x;
        }
        if(y < yMin) {
          yMin = y;
        }
        if(y > yMax) {
          yMax = y;
        }
      }else{
        p.set(x, y, color(0, 0, 0, 0));
      }
    }
  }
  return p.get(xMin, yMin, xMax - xMin, yMax - yMin);
}

PGraphics makeText(String tex) {
  PGraphics p = createGraphics(1000, 1000);
  boolean white = true;
  p.beginDraw();
  if(tex.charAt(0) == '>') {
    tex = tex.substring(1, tex.length());
    white = false;
  }
  PFont font = createFont("Impact", 128);
  float ttt = constrain(128 - tex.length(), 50, 128);
  p.textFont(font, constrain(128 - tex.length(), 50, 128));
  p.textAlign(CENTER, CENTER);
  p.textLeading(ttt);
  p.stroke(white ? 1 : 255);
  p.fill  (white ? 1 : 255);
  for(int x = -1; x < 2; x++) {
    p.pushMatrix();
    p.translate(3 * x, 0);
    p.text(tex, 0, 0, p.width, p.height);
    p.translate(-3 * x, 3 * x);
    p.text(tex, 0, 0, p.width, p.height);
    p.popMatrix();
  }
  p.stroke(white ? 255 : 1);
  p.fill  (white ? 255 : 1);
  p.text(tex, 0, 0, p.width, p.height);
  p.endDraw();
  return p;
}
PImage t, t2;
PGraphics res;
void setup() {
  surface.initOffscreen(this);
  name = args[0];
  topText = args[1].replace('~', ' ');
  bottomText = args[2].replace('~', ' ');
  width2 = int(args[3]);
  height2 = int(args[4]);
  t  = crop(makeText(topText   ));
  t2 = crop(makeText(bottomText));
  
  res = createGraphics(width2, height2);
  res.beginDraw();
  res.textAlign(CENTER);
  res.fill(255);
  res.stroke(255);
  res.imageMode(CENTER);
  float div = 4.2;
  float div2 = 1.1;
  float n = min(
    (res.width / div2) / float(t.width),
    (float(res.height) / div) / float(t.height)
  );
  res.image(t, 
    float(res.width) / 2.0, 
    (n * float(t.height)) / 1.85,
    n * float(t.width ), 
    n * float(t.height)
  );
  n = min(
    (res.width / div2) / float(t2.width),
    (float(res.height) / div) / float(t2.height)
  );
  res.image(t2, 
    float(res.width) / 2.0, 
    float(res.height) - (n * float(t2.height)) / 1.85,
    n * float(t2.width ), 
    n * float(t2.height)
  );
  res.endDraw();
  res.save(name);
  exit();
}
