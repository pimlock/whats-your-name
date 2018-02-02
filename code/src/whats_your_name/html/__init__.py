file_upload_page = '''
<!doctype html>
<html lang="en">
<head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css"
          integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <script defer src="https://use.fontawesome.com/releases/v5.0.6/js/all.js"></script>

    <title>What's Your Name?</title>

    <style type="text/css">
    </style>
</head>
<body>
<div class="container mt-2">
    <div class="row justify-content-md-center">
        <div class="col-md-10 col-lg-8">
            <div class="jumbotron">
                <h1 class="display-4 text-center">What's Your Name?!</h1>
                <p class="lead text-center">Take a photo and find out what's their name!</p>
                <div class="row">
                    <div class="col py-2">
                        <div class="media d-none" id="preview">
                            <img class="mr-3 rounded img-responsive w-50" src="" alt="Uploaded photo">
                            <div class="media-body">
                                <div id="result">
                                    <span class="loading">Checking... <i class="fas fa-circle-notch fa-spin"></i></span>
                                    <span class="name"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="w-100"></div>
                    <div class="col">
                        <form>
                            <div class="input-group mb-3">
                                <div class="custom-file">
                                    <input type="file" class="btn-primary custom-file-input" id="file">
                                    <label class="custom-file-label" for="file">Select a photo</label>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
<script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js"
        integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"
        integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
</body>

<script type="text/javascript">
    $(function () {
        var preview = $('#preview');
        var fileInput = $('#file');
        var result = $('#result');

        var getFile = function () {
            return fileInput.get(0).files[0];
        };

        fileInput.bind('change', function () {
            var reader = new FileReader();
            var file = getFile();

            reader.addEventListener("load", function () {
                preview.find('img').attr('src', reader.result);
                preview.removeClass('d-none');
                result.find('.loading').show();
                result.find('.name').text('');

                $.ajax({
                    type: 'POST',
                    data: reader.result,
                    success: function (data) {
                        result.find('.loading').hide();

                        var name = result.find('.name');
                        if (data['faces'] && data['faces'].length > 0) {
                            name.html("Found a match! It's <strong>" + data['faces'].join(', ') + "</strong>")
                        } else {
                            name.text("I didn't find a match :/")
                        }
                    },
                    error: function() {
                        result.find('.loading').hide();
                        result.find('.name').text('Something went wrong :/')
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
</html>
'''
