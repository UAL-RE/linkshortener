# linkshortener
Shorten long links using DigitalOcean Functions and an S3 backend

# Installation
Support for direct installation only (App Platform TODO)
- In the DO [Functions console](https://cloud.digitalocean.com/functions), create a new Namespace.
- Create two new functions, both using the same package name (`app`). Make sure Web Function is checked.
    - `create`
    - `r`

Edit the `create` function
- In the source code box, paste the contents of `packages/app/create/__main__.py`
- Set the runtime to the latest Python version
- Set the limits to 3 sec timeout, 128 MB memory
- Add 4 environment variables and set the values appropriately
    - `wasabi_accesskey`: Access key for bucket
    - `wasabi_secretkey`: Secret key for bucket
    - `wasabi_bucket`: Bucket name
    - `token`: Auth token to protect this function from unauthorized use
- Save

Edit the `r` function
- In the source code box, paste the contents of `packages/app/r/__main__.py`
- Repeat all of the remaining steps from the create function except adding the `token` environment variable.

# Usage
To create a new shortened link
```
<FunctionURL>/app/create?u=<long-link>&t=<token>
```

URL Parameters
- `u`: The link to shorten
- `t`: The access token specified in the Installation for the `create` function.
- `p`: An optional parameter that when set to the value `echo`, will return the shortened link as well as information about the request.

The return value will be the shortened link (in the form `<FunctionURL>/app/r?c=<code>`), a 502 HTTP code in case of an incorrect token, or an error message. Use the returned link as you would any ordinary link.

The `r` function has the form
```
<FunctionURL>/app/r?c=<code>
```

URL Parameters
- `c`: The short code that will redirect to the designated target address

If there is an error, a 500 HTTP code will be returned.



