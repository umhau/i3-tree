#include <glib/gprintf.h>
#include <i3ipc-glib/i3ipc-glib.h>

// The following packages are required for building i3-ipc:
//     libxcb and xcb-proto
//     glib >= 2.32
//     gobject-introspection (optional for bindings)
//     json-glib >= 0.14
//     gtk-doc-tools

// Or, just install it: 
// i i3ipc-glib i3ipc-glib-devel

// Compile with:
// gcc -o i3ipc.example.1 i3ipc.example.1.c $(pkg-config --libs --cflags i3ipc-glib-1.0)

gint main() {
  i3ipcConnection *conn;
  gchar *reply;

  conn = i3ipc_connection_new(NULL, NULL);

  reply = i3ipc_connection_message(conn, I3IPC_MESSAGE_TYPE_GET_TREE, "get_tree", NULL);

  g_printf("Reply: %s\n", reply);

  g_free(reply);
  g_object_unref(conn);

  return 0;
}