file_upload_page = '''
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html" charset="UTF-8">
        <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
    </head>
    <body>
        <img id="preview" src=""/>
        <form>
          <input id="file" type="file">
          <input id="go" type="button" value="Recognize!" style="display: none">
        </form>
        <div id="result"></div>
        
        <script type="text/javascript">
            $(function () {
                var goButton = $('#go');
                var preview = $('#preview');
                var fileInput = $('#file');
                var result = $('#result');
            
                var getFile = function () {
                    return fileInput.get(0).files[0];
                }
            
                fileInput.bind('change', function () {
                    var reader = new FileReader();
                    var file = getFile();
            
                    reader.addEventListener("load", function () {
                        preview.attr('src', reader.result);
                        goButton.show();
                    }, false);
            
                    if (file) {
                        reader.readAsDataURL(file);
                    }
                });
            
                goButton.bind('click', function () {
                    var reader = new FileReader();
                    var file = getFile();
            
                    reader.addEventListener("load", function () {
                        preview.attr('src', reader.result);
                            $.ajax({
                                url: '<%APP_URL%>',
                                type: 'POST',
                                data: reader.result,
                                success: function (data) {
                                    if (data['faces'] && data['faces'].length > 0) {
                                        result.html("Found a match! It's <strong>" + data['faces'].join(', ') + "</strong>")
                                    } else {
                                        result.text("I didn't find a match :/")
                                    }
                                },
                                dataType: 'json',
                                contentType: 'application/json'
                            })
                    }, false);
            
                    if (file) {
                        reader.readAsDataURL(file);
                    }
                });
            });
        </script>
    </body>
</html>
'''
