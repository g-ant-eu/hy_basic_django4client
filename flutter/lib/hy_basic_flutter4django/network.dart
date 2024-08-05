// ignore_for_file: constant_identifier_names, non_constant_identifier_names

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:html' as html;

const doLocal = String.fromEnvironment('DOLOCAL', defaultValue: 'false');
const localPort = String.fromEnvironment('LOCALPORT', defaultValue: '8000');

const WEBAPP_URL = doLocal == 'true' ? "http://localhost:$localPort/" : "../";
const NETWORKERROR_PREFIX = "ERROR:";
const KEY_USER = "user";
const KEY_PWD = "pwd";
const KEY_TOKEN = "token";

class BF4DWebServerApi {
  static String API_LOGIN = "${WEBAPP_URL}api/login/";

  /// Login to get a token using credentials.
  ///
  /// Returns a string starting with ERROR if problems arised.
  static Future<String> login(String user, String pwd, {loginUrl}) async {
    Map<String, dynamic> formData = {
      "username": user,
      "password": pwd,
    };

    final uri = Uri.parse(API_LOGIN);
    http.Response response = await csrfPost(
      uri,
      headers: {'Content-Type': 'application/json; charset=UTF-8'},
      body: json.encode(formData),
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body)['token'];
    } else {
      return NETWORKERROR_PREFIX + response.body;
    }
  }

  /// Wrapper of post to add csrf token.
  static Future<http.Response> csrfPost(Uri uri,
      {Map<String, String>? headers, Object? body, Encoding? encoding}) async {
    // add csrf token for posts
    var csrfToken = WebSession.getCsrfToken();
    if (csrfToken != null) {
      headers ??= {};
      headers["X-CSRFToken"] = csrfToken;
    }

    return await http.post(uri, headers: headers, body: body);
  }

  static Map<String, String> getTokenHeader() {
    var sessionToken = WebSession.getSessionToken();
    var requestHeaders = {"Authorization": "Token ${sessionToken!}"};
    return requestHeaders;
  }
}

/// A simple class that executes a get/put/post request to the server.
class BF4DWebCall {
  final String url;
  bool _hasError = false;
  String? errorText;
  String? responseBody;
  Map<String, dynamic>? data;
  bool isPut = false;
  bool isPost = false;
  Map<String, String>? headers;

  BF4DWebCall.get(this.url, {this.headers});

  BF4DWebCall.put(this.url, this.data, {this.headers}) {
    isPut = true;
  }

  BF4DWebCall.post(this.url, this.data, {this.headers}) {
    isPost = true;
  }

  /// Get the response from the server.
  Future<void> run() async {
    var requestHeaders = BF4DWebServerApi.getTokenHeader();
    if (headers != null) {
      requestHeaders.addAll(headers!);
    }
    try {
      http.Response response;
      if (isPut) {
        response = await http.put(Uri.parse(url),
            headers: requestHeaders, body: json.encode(data));
      } else if (isPost) {
        response = await http.post(Uri.parse(url),
            headers: requestHeaders, body: json.encode(data));
      } else {
        response = await http.get(Uri.parse(url), headers: requestHeaders);
      }
      if (response.statusCode >= 200 && response.statusCode < 300) {
        responseBody = response.body;
      } else {
        _hasError = true;
        errorText = response.body;
      }
    } catch (e) {
      _hasError = true;
      errorText = e.toString();
    }
  }

  /// Get the response from the server.
  bool hasError() {
    return _hasError;
  }

  /// Get the error text.
  String? getErrorText() {
    return errorText;
  }

  /// Get the response body.
  String? getResponseBody() {
    return responseBody;
  }

  /// Get the response body as a map.
  Map<String, dynamic>? getResponseBodyAsMap() {
    if (responseBody == null) {
      return null;
    }
    return json.decode(responseBody!);
  }
}

class WebSession {
  /// Checks credentials and returns an error message or null if login is ok.
  static Future<String?> login(String user, String password) async {
    var responseText = await BF4DWebServerApi.login(user, password);
    if (!responseText.startsWith(NETWORKERROR_PREFIX)) {
      var token = responseText;
      setSessionToken(token);
      setSessionUser(user, password);

      return null;
    } else {
      var errorMap =
          jsonDecode(responseText.replaceFirst(NETWORKERROR_PREFIX, ""));
      var errorText = errorMap['error'] ?? responseText;
      return errorText;
    }
  }

  /// Check if user is logged.
  static bool isLogged() {
    return html.window.sessionStorage[KEY_TOKEN] != null;
  }

  /// Get the user and password from the session in format [user, pwd].
  static List<String> getSessionUser() {
    return [
      html.window.sessionStorage[KEY_USER]!,
      html.window.sessionStorage[KEY_PWD]!
    ];
  }

  /// Set the user and password in the session.
  static void setSessionUser(String user, String pwd) {
    html.window.sessionStorage[KEY_USER] = user;
    html.window.sessionStorage[KEY_PWD] = pwd;
  }

  /// Set the token in the session.
  static void setSessionToken(String token) {
    html.window.sessionStorage[KEY_TOKEN] = token;
  }

  /// Get the token from the session. If not available a reload is triggered.
  static String? getSessionToken() {
    var token = html.window.sessionStorage[KEY_TOKEN];
    if (token == null) {
      html.window.location.reload();
    }
    return token;
  }

  /// Get the csrf token from the cookie.
  static String? getCsrfToken() {
    final cookie = html.document.cookie!;
    if (cookie.isEmpty) {
      return null;
    }
    final entity = cookie.split("; ").map((item) {
      final split = item.split("=");
      return MapEntry(split[0], split[1]);
    });
    final cookieMap = Map.fromEntries(entity);

    var token = cookieMap["csrftoken"];
    if (token == null) {
      throw Exception("No csrf token found.");
    }
    return token;
  }
}
