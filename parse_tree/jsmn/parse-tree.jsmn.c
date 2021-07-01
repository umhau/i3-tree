#include <i3ipc-glib/i3ipc-glib.h>
#include <stdio.h>
#include "jsmn.h"

int count_json_tokens(char *json_string) {
  
  jsmn_parser parser;
  jsmn_init(&parser);
  return jsmn_parse(&parser, json_string, strlen(json_string), NULL, 0);

}

void main() {

  i3ipcConnection  *conn;
  char            *reply;   // json string containing tree of i3 containers
  int       tokens_count;   // number of items (tokens) in the json tree

  conn         = i3ipc_connection_new    (NULL, NULL);
  reply        = i3ipc_connection_message(conn, I3IPC_MESSAGE_TYPE_GET_TREE, "get_tree", NULL);
  tokens_count = count_json_tokens(reply);

  printf("number of tokens: %d\n", tokens_count);



  jsmn_parser parser;
  jsmn_init(&parser);

  jsmntok_t tokens[tokens_count];
  int r;
  r = jsmn_parse(&parser, reply, strlen(reply), tokens, tokens_count);
  printf("r-value: %d\n", r);



  g_free(reply);
  g_object_unref(conn);

}