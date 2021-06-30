
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
