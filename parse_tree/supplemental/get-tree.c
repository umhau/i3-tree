#include <i3ipc-glib/i3ipc-glib.h>
#include <stdio.h>

void main() {

  i3ipcConnection  *conn;
  char            *reply;

  conn  = i3ipc_connection_new    (NULL, NULL);
  reply = i3ipc_connection_message(conn, I3IPC_MESSAGE_TYPE_GET_TREE, "get_tree", NULL);

  // gchar *reply =
  //   "{\"user\": \"johndoe\", \"admin\": false, \"uid\": 1000,\n  "
  //   "\"groups\": [\"users\", \"wheel\", \"audio\", \"video\"]}";

  printf("%s\n", reply);

  g_free(reply);
  g_object_unref(conn);

}