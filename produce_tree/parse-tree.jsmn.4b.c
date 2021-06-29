#include <i3ipc-glib/i3ipc-glib.h>
#include <stdio.h>
#include "jsmn.h"
#include <stdlib.h>
#include <string.h>
#include "i3tree.2.h"

#define MAXDEPTH 100


int main() {

  char * json_tree;
  int    json_tokens_count;  
  int    r;
  int    i;
  int    j;
  char * tokencontents;
  char * tokentype;
  int    depthcounter = 0;
  int    depth_list[100];

  depth_list[0] = 1;

  // json_tree           = get_i3wm_tree();
  json_tree           = get_json_file("./tree.simplified.json");
  json_tokens_count   = count_json_tokens(json_tree);

  jsmn_parser parser;
  jsmn_init(&parser);
  jsmntok_t tokens[json_tokens_count];

  r = jsmn_parse(&parser, json_tree, strlen(json_tree), tokens, json_tokens_count);

  if (r  < 0)                                  { printf("Failed to parse JSON: %d\n", r); exit(1); }
  if (r  < 1 || tokens[0].type != JSMN_OBJECT) { printf("Object expected\n");             exit(1); }
  if (r != json_tokens_count)                  { printf("Token count mismatch\n");        exit(1); }

  printf("number of tokens: %d\n", r);

  printf("[index]\t[start -> end]\t[child]\t[type]  \t[token contents]\n");

  for (i = 1; i < 30; i++) {

      printf("---------------------------------------------------------\n");

    //   printf("current start: %d | current end: %d | next start: %d\n",
    //       tokens[i + 1].start,
    //       tokens[i].end
    //   );

      

    for (j = depthcounter-1; j >= 0; j--) {

        if (depth_list[j] < tokens[i+1].start && i<1) {


        }

    }

    // if (depth_list[depthcounter-1] < tokens[i+1].start && i<1) {

    //     printf("< decreasing depth:\t[ %d <= %d ][%d] >\n", depth_list[depthcounter-1], tokens[i+1].start,depth_list[depthcounter-1] );

    //     depthcounter -- ;

    // }

    // if (tokens[i].end > tokens[i + 1].start) {

    //     // printf("DEPTH ALTERATION\n");

    //     printf("< increasing depth:\t[ %d > %d ] >\n", tokens[i].end, tokens[i + 1].start);

    //     depthcounter ++ ;

    //     depth_list[depthcounter-1] = tokens[i].end ;

    // }

    // printf("end token: %d\n", depth_list[depthcounter-1]);



    jsmntok_t *t = &tokens[i + 1];

    tokentype =     "--------";
    tokencontents = "~~~~~~~~";

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
          { char *str = json_token_tostr(json_tree, t); tokencontents=str; }
          break;

        case 4 :
          tokentype="primitive";
          { char *str = json_token_tostr(json_tree, t); tokencontents=str; }
          break;

        default :
          tokentype="INVALID";
          exit(1);
    }

    printf("[%d][ %d ]\t[depth: %d]\t[ %d -> %d ]\t[ %d ]\t[ %d:%s ]\t[ %s ]\n", 
      depth_list[depthcounter-1],
      i,
      depthcounter,
      tokens[i].start,
      tokens[i].end,
      tokens[i].size,
      tokens[i].type,
      tokentype,
      tokencontents
    );

  }

  return 0;

}