window.initializeSpeechToTextJSDemo = function (localizedResources) {
  var speak = document.getElementById('speakbtn'),
    speakli = document.getElementById('speakli'),
    stopspeak = document.getElementById('stopspeakbtn'),
    stopspeakli = document.getElementById('stopspeakli'),
    upload = document.getElementById('uploadbtn'),
    stopupload = document.getElementById('stopuploadbtn'),
    uploadli = document.getElementById('uploadli'),
    stopuploadli = document.getElementById('stopuploadli'),
    punctuationchk = document.getElementById('punctuation'),
    language = document.getElementById('langselect'),
    fileinput = document.getElementById('fileinput'),
    speechout = document.getElementById('speechout'),
    lastRecognized = '',
    recognizer,
    SpeechSDK = window.SpeechSDK,
    fileAbortCallback = null;



function recognizeOneAudioConfig(audioConfig, completionCallback) {
  var config = SpeechSDK.SpeechConfig.fromAuthorizationToken(localizedResources.token, localizedResources.region);
  config.enableDictation();

  // Turn off automatic punctation, if you really want to.
  // config.setServiceProperty('punctuation', 'explicit', SpeechSDK.ServicePropertyChannel.UriQueryParameter);

  if (language[language.selectedIndex].value !== '') {
    config.speechRecognitionLanguage = language[language.selectedIndex].value;
  }

  config.setProperty(SpeechSDK.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, '5000');
  config.setProperty(SpeechSDK.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, '5000');

  recognizer = new SpeechSDK.SpeechRecognizer(config, audioConfig);

  // The event recognizing signals that an intermediate recognition result is received.
  // You will receive one or more recognizing events as a speech phrase is recognized, with each containing
  // more recognized speech. The event will contain the text for the recognition since the last phrase was recognized.
  recognizer.recognizing = function (s, e) {
    speechout.innerHTML = lastRecognized + e.result.text;
  };

  recognizer.canceled = function (s, e) {
    var details;

    if (e.reason === SpeechSDK.CancellationReason.EndOfStream) {
      lastRecognized += '--------------------------------------------------------------------------------\r\n\r\n';
      speechout.innerHTML = lastRecognized;
    } else {
      details = SpeechSDK.CancellationDetails.fromResult(e.result);

      if (details.reason === SpeechSDK.ErrorCode.ConnectionFailure) {
        lastRecognized += localizedResources.srTryAgain;
      } else {
        lastRecognized += localizedResources.srCanceledError + e.errDetails;
      }
    }
    completionCallback();
  };

  // The event recognized signals that a final recognition result is received.
  // This is the final event that a phrase has been recognized.
  // For continuous recognition, you will get one recognized event for each phrase recognized.
  recognizer.recognized = function (s, e) {
    var resultText;

    // Indicates that recognizable speech was not detected, and that recognition is done.
    if (e.result.reason !== SpeechSDK.ResultReason.RecognizedSpeech) {
      resultText = '\r\n' + localizedResources.srComplete;
      completionCallback();
    } else {
      resultText = e.result.text;
    }

    lastRecognized += resultText + ' ';
    speechout.innerHTML = lastRecognized;
  };

  recognizer.startContinuousRecognitionAsync(function () { }, function (error) {
    if (error.includes('1006')) {
      speechout.innerHTML += localizedResources.srTryAgain;
    } else {
      speechout.innerHTML = localizedResources.srStartFailure + ' ' + error;
    }
  });
}
