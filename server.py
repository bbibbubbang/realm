from http.server import SimpleHTTPRequestHandler
import socketserver
import os

class RangeRequestHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = self.path.split('/')
            if not parts[-1]:
                return self.list_directory(path)
            else:
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, "File not found")
            return None

        try:
            fs = os.fstat(f.fileno())
            size = fs[6]
            start, end = 0, size - 1
            if 'Range' in self.headers:
                self.send_response(206)
                self.send_header('Accept-Ranges', 'bytes')
                ranges = self.headers['Range'].split('=')[1].split('-')
                start = int(ranges[0])
                if ranges[1]:
                    end = int(ranges[1])
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                size = end - start + 1
            else:
                self.send_response(200)
                self.send_header('Accept-Ranges', 'bytes')
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(size))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            if 'Range' in self.headers:
                f.seek(start)
            return f
        except:
            f.close()
            raise

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        if 'Range' in self.headers:
            ranges = self.headers['Range'].split('=')[1].split('-')
            start = int(ranges[0])
            fs = os.fstat(source.fileno())
            size = fs[6]
            end = size - 1
            if ranges[1]:
                end = int(ranges[1])
            length = end - start + 1
            outputfile.write(source.read(length))
        else:
            super().copyfile(source, outputfile)


if __name__ == "__main__":
    PORT = 8000
    Handler = RangeRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()
