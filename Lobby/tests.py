from django.test import TestCase, Client
from django.urls import reverse

from user_yamls.models import Yaml
from .models import Lobby, Slot
from django.contrib.auth.models import User

def make_user(username: str, password: str = "test123") -> User:
    return User.objects.create_user(username=username, password=password)

def make_lobby(host: User, **kwargs) -> Lobby:
    defaults = {
        "name": "Test Lobby",
        "description": "A test lobby",
        "is_async": False,
    }
    defaults.update(kwargs)
    return Lobby.objects.create(host_id=host, **defaults)

def make_yaml(owner: User, **kwargs) -> Yaml:
    defaults = {
        "slot_name": "SlotName",
        "game_name": "Game Name",
        "description": "A test game yaml",
        "game_options": "Some test yaml options",
    }
    defaults.update(kwargs)
    return Yaml.objects.create(user_id=owner, **defaults)

# Create your tests here.
class LobbyBrowserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.id = id
        self.host = make_user("host_user")
        self.other = make_user("other_user")
        self.lobby_sync = make_lobby(self.host, name="Sync Lobby", is_async=False)
        self.lobby_async = make_lobby(self.host, name="Async Lobby", is_async=True)
        self.url = reverse("Lobby:lobby_browser")

    def test_get_returns_200(self):
        """Lobby browser should always return 200, auth-ed user or not"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_all_lobbies_present_in_context(self):
        """All lobbies should be listed when no filters are applied"""
        response = self.client.get(self.url)
        self.assertIn(self.lobby_sync, response.context["lobbies"])
        self.assertIn(self.lobby_async, response.context["lobbies"])
    
    def test_get_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "Lobby/lobby_browser.html")

    def test_post_host_assigned_correctly(self):
        #checking that lobbies made by other users aren't in the host filter
        self.client.login(username="host_user", password="test123")
        other_lobby = make_lobby(self.other, name="Other Lobby")
        response = self.client.post(self.url, {"is_host": "on"})
        lobbies = list(response.context["lobbies"])
        self.assertNotIn(other_lobby, lobbies)

    #======================================================
    # Filter Tests
    #======================================================
    def test_post_filter_is_host(self):
        self.client.login(username="host_user", password="test123")
        
        #Checking if all pre-existing lobbies are in the filter
        response = self.client.post(self.url, {"is_host": "on"})
        lobbies = list(response.context["lobbies"])
        self.assertIn(self.lobby_sync, lobbies)
        self.assertIn(self.lobby_async, lobbies)

    def test_post_filter_is_host_sets_context_flag(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url, {"is_host": "on"})
        self.assertTrue(response.context.get("is_host"))


    def test_post_filter_has_joined(self):
        self.client.login(username="host_user", password="test123")
        other_lobby = make_lobby(self.other, name="Other Lobby")
        response = self.client.post(self.url, {"has_joined": "on"})
        lobbies = list(response.context["lobbies"])

        self.assertIn(self.lobby_sync, lobbies)
        self.assertNotIn(other_lobby, lobbies)

    def test_post_filter_has_joined_sets_context_flag(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url, {"has_joined": "on"})
        self.assertTrue(response.context.get("has_joined"))

    def test_post_filter_is_async(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url, {"is_async": "on"})
        lobbies = list(response.context["lobbies"])

        self.assertIn(self.lobby_async, lobbies)
        self.assertNotIn(self.lobby_sync, lobbies)

    def test_post_filter_host_and_async(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(
            self.url, 
            {"is_host": "on", "is_async": "on"}
        )
        lobbies = list(response.context["lobbies"])

        self.assertIn(self.lobby_async, lobbies)
        self.assertNotIn(self.lobby_sync, lobbies)

    def test_post_no_filter_returns_all_lobbies(self):
        self.client.login(username="host_user", password="test123")
        other_lobby = make_lobby(self.other, name="Other Lobby")
        response = self.client.post(self.url, {})
        lobbies = list(response.context["lobbies"])
        self.assertIn(self.lobby_async, lobbies)
        self.assertIn(self.lobby_sync, lobbies)
        self.assertIn(other_lobby, lobbies)
        