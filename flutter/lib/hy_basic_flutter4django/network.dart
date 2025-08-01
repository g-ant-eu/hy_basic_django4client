// ignore_for_file: constant_identifier_names, non_constant_identifier_names

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web/web.dart' as web;
import 'package:jwt_decoder/jwt_decoder.dart';

const doLocal = String.fromEnvironment('DOLOCAL', defaultValue: 'false');
const localPort = String.fromEnvironment('LOCALPORT', defaultValue: '8000');

const WEBAPP_URL = doLocal == 'true' ? "http://localhost:$localPort/" : "../";
const ADMIN = "admin/";
const NETWORKERROR_PREFIX = "ERROR:";
const KEY_USER = "user";
const KEY_PWD = "pwd";
const KEY_TOKEN = "token";
const KEY_REFRESH_TOKEN = "refresh_token";

class BF4DWebServerApi {
  static String JWT_API_LOGIN = "${WEBAPP_URL}api/token/";

  static void goToAdmin() {
    web.window.open("$WEBAPP_URL$ADMIN", 'admin');
  }

  /// Login to get a token using credentials.
  ///
  /// Returns a string starting with ERROR if problems arised.
  static Future<String> login(String user, String pwd, {loginUrl}) async {
    Map<String, dynamic> formData = {
      "username": user,
      "password": pwd,
    };

    final uri = Uri.parse(JWT_API_LOGIN);
    http.Response response = await csrfPost(
      uri,
      headers: {'Content-Type': 'application/json; charset=UTF-8'},
      body: json.encode(formData),
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      var responseBody = json.decode(response.body);
      var accessToken = responseBody['access'];
      var refreshToken = responseBody['refresh'];

      WebSession.setSessionToken(accessToken);
      WebSession.setRefreshToken(refreshToken);

      return accessToken;
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
    try {
      return await http.post(uri, headers: headers, body: body);
    } catch (e) {
      print("Error in csrfPost: $e");
      rethrow;
    }
  }

  /// Wrapper of put to add csrf token.
  static Future<http.Response> csrfPut(Uri uri,
      {Map<String, String>? headers, Object? body, Encoding? encoding}) async {
    // add csrf token for posts
    var csrfToken = WebSession.getCsrfToken();
    if (csrfToken != null) {
      headers ??= {};
      headers["X-CSRFToken"] = csrfToken;
    }
    try {
      return await http.put(uri, headers: headers, body: body);
    } catch (e) {
      print("Error in csrfPut: $e");
      rethrow;
    }
  }

  static Future<Map<String, String>> getTokenHeader(
      {bool loginAgain = false}) async {
    var sessionToken = WebSession.getSessionToken();
    if (sessionToken == null || loginAgain) {
      var userPwd = WebSession.getSessionUser();
      String res = await login(userPwd[0], userPwd[1]);
      if (res.startsWith(NETWORKERROR_PREFIX)) {
        web.window.location.reload();
        throw Exception("Error in login: $res");
      }
      sessionToken = WebSession.getSessionToken();
    }
    if (sessionToken == null) {
      throw Exception("No session token available.");
    }
    var requestHeaders = {"Authorization": "Bearer $sessionToken"};
    return requestHeaders;
  }

  static String getApiUrl(String apiPath) {
    return "${WEBAPP_URL}api/$apiPath/";
  }

  static String getUrl(String path) {
    return "$WEBAPP_URL$path/";
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
  bool doAuth = true;

  BF4DWebCall.get(this.url, {this.doAuth = true, this.headers});

  BF4DWebCall.put(this.url, this.data, {this.doAuth = true, this.headers}) {
    isPut = true;
  }

  BF4DWebCall.post(this.url, this.data, {this.doAuth = true, this.headers}) {
    isPost = true;
  }

  /// Get the response from the server.
  Future<void> run() async {
    Map<String, String> requestHeaders = {};
    if (doAuth) {
      requestHeaders = await BF4DWebServerApi.getTokenHeader();
    }
    if (headers != null) {
      requestHeaders.addAll(headers!);
    }
    try {
      http.Response response = await call(requestHeaders);
      if (response.statusCode >= 200 && response.statusCode < 300) {
        responseBody = response.body;
      } else if (response.statusCode >= 400 && response.statusCode < 500) {
        // reset token and try to login again
        WebSession.clearSessionToken();
        requestHeaders = await BF4DWebServerApi.getTokenHeader();
        if (headers != null) {
          requestHeaders.addAll(headers!);
        }
        response = await call(requestHeaders);
        if (response.statusCode >= 200 && response.statusCode < 300) {
          responseBody = response.body;
        } else {
          _hasError = true;
          errorText = response.body;
        }
      } else {
        _hasError = true;
        errorText = response.body;
      }
    } catch (e) {
      _hasError = true;
      errorText = e.toString();
    }
  }

  Future<http.Response> call(Map<String, String> requestHeaders) async {
    http.Response response;
    if (isPut) {
      response = await BF4DWebServerApi.csrfPut(Uri.parse(url),
          headers: requestHeaders, body: json.encode(data));
    } else if (isPost) {
      response = await BF4DWebServerApi.csrfPost(Uri.parse(url),
          headers: requestHeaders, body: json.encode(data));
    } else {
      response = await http.get(Uri.parse(url), headers: requestHeaders);
    }
    return response;
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

  /// Get the response body as an object (list or map).
  dynamic getResponseBodyDecoded() {
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
      try {
        var errorMap =
            jsonDecode(responseText.replaceFirst(NETWORKERROR_PREFIX, ""));
        var errorText = errorMap['error'] ?? responseText;
        return errorText;
      } on Exception catch (e) {
        return responseText.replaceFirst(NETWORKERROR_PREFIX, "");
      }
    }
  }

  /// Check if user is logged.
  static bool isLogged() {
    return web.window.sessionStorage.getItem(KEY_TOKEN) != null;
  }

  static void logout() {
    clearSessionToken();
    web.window.sessionStorage.removeItem(KEY_USER);
    web.window.sessionStorage.removeItem(KEY_PWD);
    web.window.location.reload();
  }

  /// Get the user and password from the session in format [user, pwd].
  static List<String> getSessionUser() {
    var user = web.window.sessionStorage.getItem(KEY_USER);
    var pwd = web.window.sessionStorage.getItem(KEY_PWD);
    if (user == null || pwd == null) {
      return [];
    }
    return [user, pwd];
  }

  /// Set the user and password in the session.
  static void setSessionUser(String user, String pwd) {
    web.window.sessionStorage.setItem(KEY_USER, user);
    web.window.sessionStorage.setItem(KEY_PWD, pwd);
  }

  /// Set the token in the session.
  static void setSessionToken(String token) {
    web.window.sessionStorage.setItem(KEY_TOKEN, token);
  }

  static void clearSessionToken() {
    web.window.sessionStorage.removeItem(KEY_TOKEN);
  }

  /// Get the token from the session. If not available a reload is triggered.
  ///
  /// if expired, null is returned.
  static String? getSessionToken() {
    var token = web.window.sessionStorage.getItem(KEY_TOKEN);
    if (token == null) {
      return null;
      // html.window.location.reload();
    }
    var expiryDate = JwtDecoder.getExpirationDate(token);
    if (expiryDate.isBefore(DateTime.now())) {
      return null;
    }
    return token;
  }

  static String? getRefreshToken() {
    var token = web.window.sessionStorage.getItem(KEY_REFRESH_TOKEN);
    if (token == null) {
      web.window.location.reload();
    }
    return token;
  }

  static void setRefreshToken(String token) {
    web.window.sessionStorage.setItem(KEY_REFRESH_TOKEN, token);
  }

  /// Get the csrf token from the cookie.
  static String? getCsrfToken() {
    final cookie = web.document.cookie;
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
