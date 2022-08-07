#include <stdio.h>
#include <stdlib.h>

void win(void) { system("/bin/sh"); }

void vuln() {
  char buf[64];
  setbuf(stdout, NULL);
  printf("This is almost exactly the same as jump...\n");
  gets(buf);

  while(1){

  }
}

int main(int argc, char **argv) { 

  vuln();

}
