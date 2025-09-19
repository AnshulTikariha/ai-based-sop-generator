package com.example.springcrud;

import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/posts")
public class PostController {
    private final PostRepository repo;
    public PostController(PostRepository repo) { this.repo = repo; }

    @GetMapping
    public List<Post> all() { return repo.findAll(); }

    @GetMapping("/{id}")
    public Post one(@PathVariable Long id) { return repo.findById(id).orElseThrow(); }

    @PostMapping
    public Post create(@RequestBody Post p) { return repo.save(p); }

    @PutMapping("/{id}")
    public Post update(@PathVariable Long id, @RequestBody Post p) { p.setId(id); return repo.save(p); }

    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) { repo.deleteById(id); }
}
