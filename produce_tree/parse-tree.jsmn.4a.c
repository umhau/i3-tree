#include <i3ipc-glib/i3ipc-glib.h>
#include <stdio.h>
#include "jsmn.h"
#include <stdlib.h>
#include <string.h>
#include "i3tree.1.h"

int FLIP(int zeroone) {
    if      (zeroone == 0) { zeroone=1; }
    else if (zeroone == 1) { zeroone=0; }
    return   zeroone ;
}

// TODO: use the token start/ends to skip over arrays and stay at the same level
// in the hierarchy

void main() {

  char * i3_tree;
  int    json_tokens_count;  
  int    r;
  int    i;
  char * tokencontents;
  char * tokentype;
  int    keyvalue;  // 0=key,1=value

  // i3_tree           = get_i3wm_tree();
  i3_tree           = get_json_file("./tree.simplified.json");

  json_tokens_count = count_json_tokens(i3_tree);

  jsmn_parser parser;

  jsmn_init(&parser);

  jsmntok_t tokens[json_tokens_count];

  r = jsmn_parse(&parser, i3_tree, strlen(i3_tree), tokens, json_tokens_count);

  if (r  < 0)                                  { printf("Failed to parse JSON: %d\n", r); exit(1); }
  if (r  < 1 || tokens[0].type != JSMN_OBJECT) { printf("Object expected\n");             exit(1); }
  if (r != json_tokens_count)                  { printf("Token count mismatch\n");        exit(1); }

  printf("number of tokens: %d\n", r);

  keyvalue = 0;

  for (i = 1; i < r; i++) {

    jsmntok_t *t = &tokens[i + 1];

    if (tokens[i + 1].type > 2) {

      char *str = json_token_tostr(i3_tree, t);

      tokencontents = str;

    }

    else {
      tokencontents = "object/array";
      keyvalue = FLIP(keyvalue);  
    }


    if (keyvalue == 0) {
      printf("\n[ %s :", tokencontents);
    }

    else if (keyvalue == 1) 
    {
      printf(" %s ]", tokencontents);
    }
      
    keyvalue = FLIP(keyvalue);    

  }

  exit(0);


}