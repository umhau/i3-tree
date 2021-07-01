#include <i3ipc-glib/i3ipc-glib.h>
#include <stdio.h>
#include <cjson/cJSON.h>



void main() {

  i3ipcConnection  *conn;
  char            *reply_str;

  conn  = i3ipc_connection_new    (NULL, NULL);
  reply_str = i3ipc_connection_message(conn, I3IPC_MESSAGE_TYPE_GET_TREE, "get_tree", NULL);

  // char *reply_str =
  //   "{\"user\": \"johndoe\", \"admin\": false, \"uid\": 1000,\n  "
  //   "\"groups\": [\"users\", \"wheel\", \"audio\", \"video\"]}";

  printf("%s\n", reply_str);



  // Given some JSON in a string (whether zero terminated or not), you can parse
  // it with cJSON_ParseWithLength.

  // cJSON *json = cJSON_ParseWithLength(reply_str, buffer_length);
  cJSON *json = cJSON_Parse(reply_str);

  // Given a tree of cJSON items, you can print them as a string using cJSON_Print.
  char *string = cJSON_Print(json);


  g_free(reply_str);
  g_object_unref(conn);

}