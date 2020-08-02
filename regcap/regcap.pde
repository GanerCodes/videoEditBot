PImage crop(PImage p) {
  int xMin = p.width, xMax = 0, yMin = p.height, yMax = 0;
  for(int x = 0; x < p.width; x++) {
    for(int y = 0; y < p.height; y++) {
      color cc = p.get(x, y);
      if(cc != color(255)) {
        if(x > xMax) {
          xMax = x;
        }
        if(y < yMin) {
          yMin = y;
        }
        if(x < xMin) {
          xMin = x;
        }
        if(y > yMax) {
          yMax = y;
        }
      }else{
        p.set(x, y, color(0, 0));
      }
    }
  }
  return p.get(xMin, yMin, xMax - xMin, yMax - yMin);
}

PImage addBorder(PImage in) {
  PGraphics r = createGraphics(in.width + PADX * 2, in.height + PADY * 2);
  r.beginDraw();
  r.background(255);
  r.imageMode(CENTER);
  r.image(in, r.width / 2, r.height / 2);
  r.endDraw();
  return r;
}

PGraphics p;
PImage n;
PGraphics n2;

String str = "Asians when they realize ohio exists";
String name = "temp.png";
int w = 1000;
int h = 1000;
int PADX = 12;
int PADY = 12;
int mode = 1;

void setup() {
  surface.initOffscreen(this);
  if(args != null) {
    str = args[0].replace('~', ' ').replace('^', '\n');  
    mode = int(args[4]);
    name = args[1];
    w = int(args[2]);
    h = w;
    println(args[2]);
  }
  
  p = createGraphics(1000, 1000);
  p.beginDraw();
  p.textSize(30);
  p.background(255);
  p.fill(0);
  p.strokeWeight(5);
  p.stroke(0);
  PFont f = createFont("Arial Bold", 64);
  PFont f2 = createFont("Futura Condensed Extra Bold.otf", 64);
  if(mode == 1) {
    p.textFont(f2);
    p.textAlign(CENTER);
    p.rectMode(CENTER);
    p.textSize(80 + constrain((128 - str.length()) / 3, 0, 50));
    float t = 1.75;
    for(float ox = -t; ox <= t; ox += t) {
      for(float oy = -t; oy <= t; oy += t) {
        p.pushMatrix();
        p.translate(ox, oy);
        p.text(str, p.width / 2, p.height / 2, p.width, p.height);
        p.popMatrix();
      }
    }
  }else{
    p.textFont(f);
    p.textAlign(LEFT, TOP);
    p.textSize(50 + constrain((128 - str.length()) / 1.5, 0, 50));
    p.text(str, 0, 0, p.width, p.height);
  }
  p.endDraw();
  n = crop(p);
  
  if(mode != 1) {
    n = addBorder(n);
  }
  if(mode == 1) {
    PADY = 50;
    n = addBorder(n);
  }
  float d = n.width;
  float d2 = n.height;
  if(mode != 1) {
    d = max(n.width, 1000);
  }
  
  float hr = 1000.0 / d2;
  int nh = int(1000.0 / hr);
  float rat = max((d) / float(w), (d2) / float(nh));
  
  n2 = createGraphics(w, int(d2 / rat));
  n2.beginDraw();
  n2.background(255);
  
  float iw = n.width  / rat;
  float ih = n.height / rat;
  
  if(mode == 1) {
    n2.imageMode(CENTER);
    n2.image(n, n2.width / 2, n2.height / 2, iw / 1.1, ih / 1.1);
  }else{
    n2.image(n, 0, 0, iw, ih);
  }
  n2.endDraw();
  n2.save(name);
  exit();
}
