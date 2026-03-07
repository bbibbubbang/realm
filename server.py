from http.server import SimpleHTTPRequestHandler
import socketserver
import os

class RangeRequestHandler(SimpleHTTPRequestHandler):
    def parse_range_header(self, size):
        range_header = self.headers.get('Range')
        if not range_header or not range_header.startswith('bytes='):
            return None

        try:
            ranges = range_header.split('=')[1].split(',')
            if len(ranges) > 1:
                return None # We only support single range for now

            range_str = ranges[0].strip()
            if '-' not in range_str:
                return None

            start_str, end_str = range_str.split('-', 1)
            start_str = start_str.strip()
            end_str = end_str.strip()

            if not start_str:
                # -suffix-length
                if not end_str:
                    return None
                suffix = int(end_str)
                start = max(0, size - suffix)
                end = size - 1
            else:
                start = int(start_str)
                if not end_str:
                    end = size - 1
                else:
                    end = int(end_str)

            if start < 0 or start >= size or (end is not None and start > end):
                return None

            end = min(end, size - 1)
            return start, end
        except (ValueError, IndexError):
            return None

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
            self.range_data = None
            if 'Range' in self.headers:
                self.range_data = self.parse_range_header(size)
                if self.range_data:
                    start, end = self.range_data
                    self.send_response(206)
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                    size = end - start + 1
                else:
                    self.send_response(200)
                    self.send_header('Accept-Ranges', 'bytes')
            else:
                self.send_response(200)
                self.send_header('Accept-Ranges', 'bytes')
            self.send_header("Content-type", ctype)
            self.send_header("Content-Length", str(size))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            if self.range_data:
                f.seek(self.range_data[0])
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
        if hasattr(self, 'range_data') and self.range_data:
            start, end = self.range_data
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
