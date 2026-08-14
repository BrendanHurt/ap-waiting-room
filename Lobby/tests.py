from django.test import TestCase, Client
from django.urls import reverse
import datetime

from user_yamls.models import Yaml
from .models import Lobby, Slot
from django.contrib.auth.models import User
from guardian.shortcuts import get_objects_for_user

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
        self.lobby_sync_join_url = reverse("Lobby:join_lobby", args=(self.lobby_sync.id,))
        self.url = reverse("Lobby:lobby_browser")

    def test_get_returns_200(self):
        """Lobby browser should always return 200, auth-ed user or not"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_join_redirects_unauthenticated(self):
        response = self.client.get(self.lobby_sync_join_url)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={self.lobby_sync_join_url}",
            fetch_redirect_response=False
        )

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
        
    def test_post_filter_is_async_with_unauthenticated(self):
        response = self.client.post(self.url, {"is_async": "on"})
        lobbies = list(response.context["lobbies"])

        self.assertIn(self.lobby_async, lobbies)
        self.assertNotIn(self.lobby_sync, lobbies)

    def test_post_all_filters_with_unauthenticated_returns_200(self):
        response = self.client.post(
            self.url, 
            {"is_host": "on", "has_joined": "on", "is_async": "on"}
        )
        self.assertEqual(response.status_code, 200)

class LobbyFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.id = id
        self.host = make_user(username="host_user", password="test123")
        self.other = make_user(username="other_user", password="test123")
        self.url = reverse("Lobby:lobby_form")
        self.lobby = make_lobby(self.host, name="Existing Lobby")
        self.submit_url = reverse("Lobby:submit_lobby")
    
    def _lobby_form_for(self, lobby_id):
        return reverse(
            "Lobby:lobby_form", 
            kwargs = {"lobby_id": lobby_id},
        )

    def test_post_uses_correct_template(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url, {})
        self.assertTemplateUsed(response, "Lobby/manage_lobby_form.html")

    def test_get_create_form_redirects_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertRedirects(
            response,
            f"{reverse('users:login')}?next={self.url}",
            fetch_redirect_response=False,
        )
        
    #=================================================
    # Creating a new lobby
    def test_create_form_renders_for_authenticated_user(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "Lobby/manage_lobby_form.html")

    def test_create_form_context_has_no_lobby_id(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url)
        self.assertIsNone(response.context.get("lobby_id"))

    def test_create_form_context_contains_defaults(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url)
        self.assertEqual(
            response.context.get("lobby_name"), 
            Lobby._meta.get_field("name").get_default()
        )
        #Can't be checked for equality, so just see if it's there
        self.assertIn("lobby_start_date", response.context)
        self.assertEqual(
            response.context.get("lobby_description"), 
            Lobby._meta.get_field("description").get_default()
        )
        self.assertEqual(
            response.context.get("lobby_async"), 
            Lobby._meta.get_field("is_async").get_default()
        )

    #=================================================
    # Editing an existing lobby
    def test_edit_form_renders_with_lobby_data(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.get(self._lobby_form_for(self.lobby.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.lobby.name,
            response.context.get("lobby_name")
        )
        self.assertIn("lobby_start_date", response.context)
        self.assertEqual(
            self.lobby.description,
            response.context.get("lobby_description")
        )
        self.assertEqual(
            self.lobby.is_async,
            response.context.get("lobby_async")
        )

    def test_edit_form_returns_404_for_nonexistent_lobby(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.get(reverse(
            "Lobby:lobby_form",
            kwargs={"lobby_id": 999999}
        ))
        print(response)
        self.assertEqual(response.status_code, 404)

    def test_edit_form_redirects_unauthenticated(self):
        form_url = self._lobby_form_for(self.lobby.id)
        response = self.client.get(form_url)
        self.assertRedirects(
            response,
            f"{reverse("users:login")}?next={form_url}",
            fetch_redirect_response=False
        )

class SubmitLobbyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.host_user = make_user(username="host_user", password="test123")
        self.url = reverse("Lobby:submit_lobby")
        self.valid_payload = {
            "name": "Test Lobby",
            "start_date": "2026-7-1",
            "description": "Description for test lobby",
            "is_async": False,
            "next": reverse("Lobby:lobby_form")
        }
    
    def _update_url(self, lobby_id):
        return reverse("Lobby:submit_lobby", kwargs={"lobby_id": lobby_id})

    #=================================================
    # Creating a new lobby
    def test_create_redirects_to_browser(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"{reverse('Lobby:lobby_browser')}",
            fetch_redirect_response = False
        )

    def test_create_lobby_persists_to_database(self):
        self.client.login(username="host_user", password="test123")
        count_before = Lobby.objects.count()
        response = self.client.post(self.url, self.valid_payload)
        self.assertEqual(count_before + 1, Lobby.objects.count())

    def test_create_lobby_sets_host_to_requesting_user(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url, self.valid_payload)
        lobby = Lobby.objects.get(name="Test Lobby")
        self.assertEqual(self.host_user, lobby.host_id)

    def test_create_lobby_assigns_host_permissions(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self.url, self.valid_payload)
        lobby = Lobby.objects.get(name="Test Lobby")
        self.assertEqual(
            self.host_user.has_perm("change_lobby", lobby),
            True
        )
        self.assertEqual(
            self.host_user.has_perm("delete_lobby", lobby),
            True
        )
        self.assertEqual(
            self.host_user.has_perm("view_lobby", lobby),
            True
        )

    def test_create_lobby_is_async_false_when_omitted(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(
            self.url,
            {
                "name": "None Async Test",
                "start_date": "2026-7-1",
                "description": "Won't have async"
            }
        )
        lobby = Lobby.objects.get(name="None Async Test")
        self.assertEqual(lobby.is_async, False)

    def test_create_lobby_is_async_true_when_provided(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(
            self.url, 
            {
                "name": "Async Test",
                "start_date": "2026-7-1",
                "description": "Description for test async lobby",
                "is_async": True,
            }
        )
        lobby = Lobby.objects.get(name="Async Test")
        self.assertEqual(lobby.is_async, True)

    def test_unauthenticated_create_redirects_to_login(self):
        response = self.client.post(self.url, self.valid_payload)

        self.assertRedirects(
            response,
            f"{reverse('users:login')}",
            fetch_redirect_response = False
        )
    
    def test_unauthenticated_create_carries_over_context(self):
        response = self.client.post(self.url, self.valid_payload)

        self.assertEqual(response["next"], self.valid_payload["next"])
    
    #=================================================
    # Creating a new lobby

    def test_update_lobby_changes_name(self):
        self.client.login(username="host_user", password="test123")
        lobby = make_lobby(self.host_user, name="Old Name")

        payload = {**self.valid_payload, "name": "New Name"}
        self.client.post(self._update_url(lobby.id), payload)

        lobby.refresh_from_db()

        self.assertEqual(lobby.name, payload["name"])

    def test_update_lobby_changes_description(self):
        self.client.login(username="host_user", password="test123")
        lobby = make_lobby(
            self.host_user,
            description=self.valid_payload["description"]
        )
        new_payload = {
            **self.valid_payload,
            "description": "Updated description"
        }
        self.client.post(self._update_url(lobby.id), new_payload)
        lobby.refresh_from_db()
        self.assertEqual(lobby.description, new_payload["description"])

    def test_update_lobby_changes_async(self):
        self.client.login(username="host_user", password="test123")
        lobby = make_lobby(
            self.host_user,
            is_async=True
        )
        new_payload = {
            **self.valid_payload,
            "is_async": False
        }
        self.client.post(
            self._update_url(lobby.id),
            new_payload    
        )
        lobby.refresh_from_db()
        self.assertEqual(lobby.is_async, new_payload["is_async"])

    def test_update_lobby_changes_start_date(self):
        self.client.login(username="host_user", password="test123")
        lobby = make_lobby(
            self.host_user, 
            start_date=datetime.date.fromisoformat("2026-07-01")
        )
        new_payload = {
            **self.valid_payload,
            "start_date": datetime.date.fromisoformat("2026-07-02")
        }
        self.client.post(self._update_url(lobby.id), new_payload)
        lobby.refresh_from_db()

        self.assertEqual(
            lobby.start_date,
            new_payload["start_date"]
        )

    def test_update_lobby_returns_404_for_nonexistent_lobby(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.post(self._update_url(9999), self.valid_payload)
        self.assertEqual(response.status_code, 404)

    def test_update_lobby_does_not_change_host(self):
        self.client.login(username="host_user", password="test123")
        lobby = make_lobby(self.host_user, name="Old Name")

        new_payload = {**self.valid_payload, "name": "New Name"}
        self.client.post(self._update_url(lobby.id), new_payload)
        lobby.refresh_from_db()

        self.assertEqual(lobby.host_id, self.host_user)



class DeleteLobbyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.host_user = make_user(username="host_user", password="test123")
        self.lobby = make_lobby(self.host_user)

    def _url(self, lobby_id=None):
        return reverse(
            "Lobby:delete_lobby",
            kwargs={"lobby_id": lobby_id or self.lobby.id}
        )

    def test_delete_removes_lobby(self):
        self.client.login(username="host_user", password="test123")
        self.client.get(self._url())
        self.assertFalse(Lobby.objects.filter(pk=self.lobby.id).exists())

    def test_delete_redirects_to_browser(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("Lobby:lobby_browser"))

    def test_delete_nonexistent_lobby_raises_404(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.get(self._url(9999))    
        self.assertEqual(response.status_code, 404)

    def test_delete_lobby_cascades_to_slots(self):
        self.client.login(username="host_user", password="test123")
        yaml = make_yaml(self.host_user)
        Slot.objects.create(lobby_id=self.lobby, slot_id=yaml)
        self.client.get(self._url())
        remaining_slots = Slot.objects.filter(lobby_id=self.lobby)
        self.assertFalse(remaining_slots.exists())

    def test_delete_lobby_doesnt_impact_other_lobbies(self):
        self.client.login(username="host_user", password="test123")
        yaml = make_yaml(self.host_user)
        other_lobby = make_lobby(self.host_user)
        Slot.objects.create(lobby_id=self.lobby, slot_id=yaml)
        Slot.objects.create(lobby_id=other_lobby, slot_id=yaml)
        self.client.get(self._url())
        remaining_slots = Slot.objects.filter(lobby_id=other_lobby)
        self.assertTrue(remaining_slots.exists())
        
class ViewLobbyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.host_user = make_user(username="host_user", password="test123")
        self.lobby = make_lobby(self.host_user)
        
    def _url(self, lobby_id):
        return (reverse(
            "Lobby:view_lobby", 
            kwargs={"lobby_id": lobby_id}
        ))

    def test_view_lobby_uses_correct_template(self):
        response = self.client.get(self._url(self.lobby.id))
        self.assertTemplateUsed(response, "Lobby/view_lobby.html")

    def test_view_lobby_returns_200(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.get(self._url(self.lobby.id))
        self.assertEqual(response.status_code, 200)

    def test_view_lobby_returns_404_for_nonexistent_lobby(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.get(self._url(99999))
        self.assertEqual(response.status_code, 404)

    def test_new_lobby_contains_empty_slot_list(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.get(self._url(self.lobby.id))
        self.assertEqual(list(response.context["slots"]), [])
    
    #Testing that context gets sent over
    def test_view_lobby_context_contains_slots(self):
        self.client.login(username="host_user", password="test123")
        yaml = make_yaml(self.host_user)
        slot = Slot.objects.create(lobby_id=self.lobby, slot_id=yaml)
        response = self.client.get(self._url(self.lobby.id))
        self.assertIn(slot, list(response.context["slots"]))

    def test_view_lobby_context_contains_lobby(self):
        self.client.login(username="host_user", password="test123")
        response = self.client.get(self._url(self.lobby.id))
        self.assertEqual(response.context["lobby"], self.lobby)

    

