#include <stdio.h>
#include <stdlib.h>


// Tests overflows And format strings
void set_name() {
  char buf[500];
  setbuf(stdout, NULL);
  printf("Set your name!...\n");
  gets(buf);
  printf(buf);
}

int main(int argc, char **argv) { set_name(); }
