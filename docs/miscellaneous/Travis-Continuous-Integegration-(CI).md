1. I installed [The Travis Client](https://github.com/travis-ci/travis.rb#readme) with `gem install travis`, which requires Ruby.
(I'm using the tool [rbenv](https://github.com/rbenv/rbenv)).

2. I signed in, with `travis login`

3. I followed [these instructions](https://oncletom.io/2016/travis-ssh-deploy/) to:
    
    1. Generate a dedicated SSH key (it is easier to isolate and to revoke);
    2. Encrypt the private key to make it readable only by Travis CI (so as we can commit safely too!);
    3. Copy the public key onto the remote SSH host;
    4. Cleanup after unnecessary files;
    5. Stage the modified files into Git.
   
    This looks like this:
    
    ```bash
    # generate key
    ssh-keygen -t rsa -b 4096 -C 'build@travis-ci.org' -f ./deploy_rsa
 
    # Encrypt file for Travis
    travis encrypt-file deploy_rsa --add
 
    # Add key to server
    ssh-copy-id -i deploy_rsa.pub <ssh-user>@<deploy-host>
    
    # Remove non-encryped keys, add encryped key to git
    rm -f deploy_rsa deploy_rsa.pub
    git add deploy_rsa.enc .travis.yml
    ```

I modified to `.travis.yml` file to ssh into the server after tests pass, by adding this code:

```bash
after_success:
  - eval "$(ssh-agent -s)" #start the ssh agent
  - chmod 600 .travis/deploy_rsa.enc # this key should have push access
  - ssh-add travis/deploy_rsa.enc
  - git remote add deploy energycomps.its.carleton.edu
  - git push deploy
```

The `--add` flag in the step above automaticlly added this to `.travis.yml` file, which decodes the key:

```bash
before_install:
  - openssl aes-256-cbc -K $encrypted_26d5205ad747_key -iv $encrypted_26d5205ad747_iv
-in deploy_rsa.enc -out deploy_rsa -d
```
