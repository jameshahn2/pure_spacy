const displacy = new displaCy('http://localhost:8080', {
  container: '#displacy',
});

function parse(text) {
  displacy.parse(text)
}

