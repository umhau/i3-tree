#include <i3ipc-glib/i3ipc-glib.h>
#include <stdio.h>
#include "jsmn.h"
#include <stdlib.h>
#include <string.h>
#include "i3tree.1.h"


void main() {

  char * i3_tree;
  int    json_tokens_count;  
  int    r;
  int    i;
  char * tokencontents;
  char * tokentype;
  // int    keyvalue;  // 0=key,1=value

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

  printf("[index]\t[start -> end]\t[child]\t[type]  \t[token contents]\n");

  for (i = 1; i < 50; i++) {

    jsmntok_t *t = &tokens[i + 1];

    tokentype =     "--------";
    tokencontents = "~~~~~~~~";

    // if (tokens[i + 1].type > 2) {
    //   keyvalue=
    // }

    switch(tokens[i + 1].type) {

        case 0 :
          tokentype="undefined";
          break;

        case 1 :
          tokentype="object";
          break;

        case 2 :
          tokentype="array";
          break;

        case 3 :
          tokentype="string";
          {
          char *str = json_token_tostr(i3_tree, t);
          // printf("contents:           %s\n", str);
          tokencontents=str;
          }
          break;

        case 4 :
          tokentype="primitive";
          {
          char *str = json_token_tostr(i3_tree, t);
          // printf("contents:           %s\n", str);
          tokencontents=str;
          }
          break;

        default :
          tokentype="INVALID";
          exit(1);
    }

    // printf("token type:         %d\n", tokens[i + 1].type);

    // printf("node bool:          %d\n", jsoneq(i3_tree, &tokens[i], "nodes") );



    printf("[ %d ]\t[ %d -> %d ]\t[ %d ]\t[ %d:%s ]\t[ %s ]\n", 
      i,
      tokens[i + 1].start,
      tokens[i + 1].end,
      tokens[i + 1].size,
      tokens[i + 1].type,
      tokentype,
      tokencontents
    );
    


    // if (jsoneq(i3_tree, &tokens[i], "nodes") == 0) { 
    //   printf("contents: %.*s\n",  tokens[i + 1].end - tokens[i + 1].start);
    // }

    // printf("token type: %s\n", tokens[i + 1].type);
    // printf("token: %d\n");
      
    // if (jsoneq(i3_tree, &tokens[i], "nodes") == 0) {

    //   printf("- User: %.*s\n", tokens[i + 1].end - tokens[i + 1].start, i3_tree + tokens[i + 1].start);
    // //   i++;
      
    // }

  }

  exit(0);

  /* Loop over all keys of the root object */
  for (i = 1; i < r; i++) {
      
    if (jsoneq(i3_tree, &tokens[i], "nodes") == 0) {

      printf("- User: %.*s\n", tokens[i + 1].end - tokens[i + 1].start, i3_tree + tokens[i + 1].start);
      i++;

    }

    else {

      continue;    
      printf("Unexpected key: %.*s\n", tokens[i].end - tokens[i].start, i3_tree + tokens[i].start);

    }

  }

}