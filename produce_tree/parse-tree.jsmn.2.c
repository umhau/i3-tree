#include <i3ipc-glib/i3ipc-glib.h>
#include <stdio.h>
#include "jsmn.h"
#include <stdlib.h>
#include <string.h>

char * get_i3wm_tree() {

  i3ipcConnection  *conn;
  char            *reply;   // json string containing tree of i3 containers

  conn         = i3ipc_connection_new    (NULL, NULL);
  reply        = i3ipc_connection_message(conn, I3IPC_MESSAGE_TYPE_GET_TREE, "get_tree", NULL);

  g_object_unref(conn);

  return reply;

}

int count_json_tokens(char *json_string) {
  
  jsmn_parser parser;
  jsmn_init(&parser);
  return jsmn_parse(&parser, json_string, strlen(json_string), NULL, 0);

}

static int jsoneq(const char *json, jsmntok_t *tok, const char *s) {
  if (tok->type == JSMN_STRING && (int)strlen(s) == tok->end - tok->start &&
      strncmp(json + tok->start, s, tok->end - tok->start) == 0) {
    return 0;
  }
  return -1;
}

char * json_token_tostr(char *js, jsmntok_t *t)
{
  js[t->end] = '\0';
  return js + t->start;
}

char * get_json_file(char * filename) {

	FILE          * filepointer;
  #define       filesize 100000
	static char   buffer[filesize];

	filepointer = fopen(  filename,"r");
	fread(                buffer, filesize, 1, filepointer);
	fclose(               filepointer);

  return buffer;

}



void main() {

  char * i3_tree;
  int    json_tokens_count;  
  int    r;
  int    i;

  // i3_tree           = get_i3wm_tree();
  i3_tree           = get_json_file("./tree.simplified.json");
  json_tokens_count = count_json_tokens(i3_tree);

  jsmn_parser parser;
  jsmn_init(&parser);

  jsmntok_t tokens[json_tokens_count];

  r = jsmn_parse(&parser, i3_tree, strlen(i3_tree), tokens, json_tokens_count);

  if (r < 0)                                  { printf("Failed to parse JSON: %d\n", r); exit(1); }
  if (r < 1 || tokens[0].type != JSMN_OBJECT) { printf("Object expected\n");             exit(1); }

  printf("number of detected tokens:  %d\n", json_tokens_count);
  printf("number of extracted tokens: %d\n", r);

  for (i = 1; i < 25; i++) {

    jsmntok_t *t = &tokens[i + 1];

    printf("-- [ %d ] -------------------------------------------\n", i);
    printf("start:              %d\n", tokens[i + 1].start);
    printf("end:                %d\n", tokens[i + 1].end  );
    printf("number of children: %d\n", tokens[i + 1].size);
    
    switch(tokens[i + 1].type) {

        case 0 :
          printf("type:               undefined\n" );
          break;

        case 1 :
          printf("type:               object\n");
          break;

        case 2 :
          printf("type:               array\n" );
          break;

        case 3 :
          printf("type:               string\n" );
          {
          char *str = json_token_tostr(i3_tree, t);
          printf("contents:           %s\n", str);
          }
          break;

        case 4 :
          printf("type:               primitive\n" );
          {
          char *str = json_token_tostr(i3_tree, t);
          printf("contents:           %s\n", str);
          }
          break;

        default :
          printf("something else\n" );
    }

    printf("token type:         %d\n", tokens[i + 1].type);

    printf("node bool:          %d\n", jsoneq(i3_tree, &tokens[i], "nodes") );

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