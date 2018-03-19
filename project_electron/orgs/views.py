# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decimal import *
import json

from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, UpdateView, CreateView, DetailView, TemplateView, View

from orgs.models import Archives, Organization, User, BagItProfile
from orgs.form import *
from orgs.authmixins import *

from rights.models import RightsStatement

from transfer_app.mixins import JSONResponseMixin

class OrganizationCreateView(ManagingArchivistMixin, SuccessMessageMixin, CreateView):
    template_name = 'orgs/create.html'
    model = Organization
    fields = ['name', 'acquisition_type']
    success_message = "New Organization Saved!"

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Add Organization'
        context['acquisition_types'] = Organization.ACQUISITION_TYPE_CHOICES
        return context

    def get_success_url(self):
        return reverse('orgs-detail', kwargs={'pk': self.object.pk})


class OrganizationDetailView(OrgReadViewMixin, DetailView):
    template_name = 'orgs/detail.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationDetailView, self).get_context_data(**kwargs)
        context['meta_page_title'] = self.object.name
        context['uploads'] = []
        archives = Archives.objects.filter(process_status__gte=20, organization=context['object']).order_by('-created_time')[:15]
        for archive in archives:
            archive.bag_info_data = archive.get_bag_data()
            context['uploads'].append(archive)
        context['uploads_count'] = Archives.objects.filter(process_status__gte=20, organization=context['object']).count()
        return context


class OrganizationEditView(ManagingArchivistMixin, SuccessMessageMixin, UpdateView):
    template_name = 'orgs/update.html'
    model =         Organization
    fields =        ['is_active','name', 'acquisition_type']
    success_message = "Organization Saved!"

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Edit Organization'
        context['acquisition_types'] = Organization.ACQUISITION_TYPE_CHOICES
        return context

    def get_success_url(self):
        return reverse('orgs-detail', kwargs={'pk': self.object.pk})


class OrganizationListView(ArchivistMixin, ListView):

    template_name = 'orgs/list.html'
    model = Organization

    def get_context_data(self, **kwargs):
        context = super(OrganizationListView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Organizations'
        return context


class UsersListView(ArchivistMixin, ListView):
    template_name = 'orgs/users/list.html'
    model = User

    def get_context_data(self, **kwargs):
        context = super(UsersListView, self).get_context_data(**kwargs)

        context['meta_page_title'] = 'Users'

        refresh_ldap = User.refresh_ldap_accounts()
        if refresh_ldap:
            messages.info(self.request, '{} new accounts were just synced!'.format(refresh_ldap))

        context['users_list'] = [{'org' : {}, 'users' : []}]
        context['users_list'][0]['org'] = {'pass':'pass'}
        context['users_list'][0]['users'] = User.objects.all().order_by('username')

        context['org_users_list'] = [{'org' : {}, 'users' : []}]
        context['org_users_list'] = Organization.users_by_org()

        context['next_unassigned_user'] = User.objects.filter(from_ldap=True,is_new_account=True,organization=None).order_by('username').first()

        return context


class UsersCreateView(ManagingArchivistMixin, SuccessMessageMixin, CreateView):
    template_name = 'orgs/users/update.html'
    model = User
    fields = ['is_new_account']
    success_message = "New User Saved!"

    def get_form_class(self):
        return (OrgUserUpdateForm)

    def get_success_url(self):
        return reverse('users-detail', kwargs={'pk': self.object.pk})


class UsersDetailView(OrgReadViewMixin, DetailView):
    template_name = 'orgs/users/detail.html'
    model = User
    def get_context_data(self, **kwargs):
        context = super(UsersDetailView, self).get_context_data(**kwargs)
        context['meta_page_title'] = self.object.username
        context['uploads'] = []
        archives = Archives.objects.filter(process_status__gte=20, organization = context['object'].organization).order_by('-created_time')[:5]
        for archive in archives:
            archive.bag_info_data = archive.get_bag_data()
            context['uploads'].append(archive)
        context['uploads_count'] = Archives.objects.filter(process_status__gte=20, organization = context['object'].organization).count()
        return context


class UsersEditView(ManagingArchivistMixin, SuccessMessageMixin, UpdateView):
    template_name = 'orgs/users/update.html'
    model = User
    page_title = "Edit User"
    success_message = "Your changes have been saved!"

    def get_form_class(self):
        return (RACSuperUserUpdateForm if self.object.is_staff else OrgUserUpdateForm)

    def get_context_data(self, **kwargs):
        context = super(UsersEditView, self).get_context_data(**kwargs)
        context['page_title'] = "Edit User"
        context['meta_page_title'] = "Edit User"
        return context

    def get_success_url(self):
        return reverse('users-detail', kwargs={'pk': self.object.pk})


class UserPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'orgs/users/password_change.html'
    model = User
    success_message = "New password saved."
    form_class = UserPasswordChangeForm

    def get_context_data(self,**kwargs):
        context = super(UserPasswordChangeView, self).get_context_data(**kwargs)
        context['meta_page_title'] = 'Change Password'
        return context

    def get_success_url(self):
        return reverse('users-detail', kwargs={'pk': self.request.user.pk})

class BagItProfileManageView(View):
    template_name = 'orgs/bagit_profiles/manage.html'
    model = BagItProfile

    def get(self, request, *args, **kwargs):
        applies_to_organization = Organization.objects.get(pk=self.kwargs.get('pk'))
        source_organization = self.request.user.organization
        profile = None
        if 'profile_pk' in kwargs:
            profile = get_object_or_404(BagItProfile, pk=self.kwargs.get('profile_pk'))
            form = BagItProfileForm(instance=profile)
        else:
            form = BagItProfileForm(
                initial={
                    'applies_to_organization': applies_to_organization,
                    'source_organization': source_organization,
                    'contact_email': 'archive@rockarch.org',
                }
            )
        bag_info_formset = BagItProfileBagInfoFormset(instance=profile, prefix='bag_info')
        manifests_formset = ManifestsRequiredFormset(instance=profile, prefix='manifests')
        serialization_formset = AcceptSerializationFormset(instance=profile, prefix='serialization')
        version_formset = AcceptBagItVersionFormset(instance=profile, prefix='version')
        tag_manifests_formset = TagManifestsRequiredFormset(instance=profile, prefix='tag_manifests')
        tag_files_formset = TagFilesRequiredFormset(instance=profile, prefix='tag_files')
        return render(request, self.template_name, {
            'form': form,
            'bag_info_formset': bag_info_formset,
            'manifests_formset': manifests_formset,
            'serialization_formset': serialization_formset,
            'version_formset': version_formset,
            'tag_manifests_formset': tag_manifests_formset,
            'tag_files_formset': tag_files_formset,
            'meta_page_title': 'BagIt Profile',
            'organization': applies_to_organization,
            })

    def post(self, request, *args, **kwargs):
        instance = None
        if self.kwargs.get('profile_pk'):
            instance = get_object_or_404(BagItProfile, pk=self.kwargs.get('profile_pk'))
        form = BagItProfileForm(request.POST, instance=instance)
        if form.is_valid():
            bagit_profile = form.save()
            bag_info_formset = BagItProfileBagInfoFormset(request.POST, instance=bagit_profile, prefix='bag_info')
            manifests_formset = ManifestsRequiredFormset(request.POST, instance=bagit_profile, prefix='manifests')
            serialization_formset = AcceptSerializationFormset(request.POST, instance=bagit_profile, prefix='serialization')
            version_formset = AcceptBagItVersionFormset(request.POST, instance=bagit_profile, prefix='version')
            tag_manifests_formset = TagManifestsRequiredFormset(request.POST, instance=bagit_profile, prefix='tag_manifests')
            tag_files_formset = TagFilesRequiredFormset(request.POST, instance=bagit_profile, prefix='tag_files')
            forms_to_save = [bag_info_formset, manifests_formset, serialization_formset, version_formset, tag_manifests_formset, tag_files_formset]
            for formset in forms_to_save:
                if formset.is_valid():
                    formset.save()
                else:
                    return render(request, self.template_name, {
                        'form': bagit_profile,
                        'bag_info_formset': bag_info_formset,
                        'manifests_formset': manifests_formset,
                        'serialization_formset': serialization_formset,
                        'version_formset': version_formset,
                        'tag_manifests_formset': tag_manifests_formset,
                        'tag_files_formset': tag_files_formset,
                        'meta_page_title': 'BagIt Profile',
                        })
            bagit_profile.version = bagit_profile.version + Decimal(0.1)
            bagit_profile.bagit_profile_identifier = request.build_absolute_uri(reverse('bagit-profiles-json', args=(bagit_profile.applies_to_organization.pk, bagit_profile.pk)))
            bagit_profile.save()
            return redirect('orgs-detail', bagit_profile.applies_to_organization.pk)
        return render(request, self.template_name, {
            'form': form,
            'bag_info_formset': BagItProfileBagInfoFormset(request.POST, prefix='bag_info'),
            'manifests_formset': ManifestsRequiredFormset(request.POST, prefix='manifests'),
            'serialization_formset': AcceptSerializationFormset(request.POST, prefix='serialization'),
            'version_formset': AcceptBagItVersionFormset(request.POST, prefix='version'),
            'tag_manifests_formset': TagManifestsRequiredFormset(request.POST, prefix='tag_manifests'),
            'tag_files_formset': TagFilesRequiredFormset(request.POST, prefix='tag_files'),
            'meta_page_title': 'BagIt Profile',
            })

class BagItProfileJSONView(JSONResponseMixin, TemplateView):

    def render_to_response(self, context, **kwargs):
        obj = get_object_or_404(BagItProfile,pk=context['profile_pk'])
        bag_info_obj = BagItProfileBagInfo.objects.filter(bagit_profile=obj)
        manifests_obj = ManifestsRequired.objects.filter(bagit_profile=obj)
        serialization_obj = AcceptSerialization.objects.filter(bagit_profile=obj)
        version_obj = AcceptBagItVersion.objects.filter(bagit_profile=obj)
        tag_manifests_obj = TagManifestsRequired.objects.filter(bagit_profile=obj)
        tag_files_obj = TagFilesRequired.objects.filter(bagit_profile=obj)

        resp = {}
        resp['BagIt-Profile-Info'] = {}
        resp['BagIt-Profile-Info']['BagIt-Profile-Identifier'] = getattr(obj, 'bagit_profile_identifier', None)
        resp['BagIt-Profile-Info']['Source-Organization'] = getattr(obj, 'source_organization.name', None)
        resp['BagIt-Profile-Info']['External-Description'] = getattr(obj, 'external_descripton', None)
        resp['BagIt-Profile-Info']['Version'] = getattr(obj, 'version', None)
        resp['BagIt-Profile-Info']['Contact-Name'] = getattr(obj, 'contact_name', None)
        resp['BagIt-Profile-Info']['Contact-Email'] = getattr(obj, 'contact_email', None)
        resp['BagIt-Profile-Info']['Contact-Phone'] = getattr(obj, 'contact_phone', None)

        resp['Allow-Fetch.txt'] = getattr(obj, 'allow_fetch', None)
        resp['Serialization'] = getattr(obj, 'serialization', None)

        resp['Bag-Info'] = {}
        for bi in bag_info_obj:
            resp['Bag-Info'][bi.get_field_display()] = {}
            resp['Bag-Info'][bi.get_field_display()]['required'] = bi.required
            resp['Bag-Info'][bi.get_field_display()]['repeatable'] = bi.repeatable
            resp['Bag-Info'][bi.get_field_display()]['values'] = []
            values = BagItProfileBagInfoValues.objects.filter(bagit_profile_baginfo=bi)
            for v in values:
                resp['Bag-Info'][bi.get_field_display()]['values'].append(v.values)

        resp['Manifests-Required'] = []
        for m in manifests_obj:
            resp['Manifests-Required'].append(m.name)

        resp['Accept-Serialization'] = []
        for s in serialization_obj:
            resp['Accept-Serialization'].append(s.name)

        resp['Accept-BagIt-Version'] = []
        for v in version_obj:
            resp['Accept-BagIt-Version'].append(v.name)

        resp['Tag-Manifests-Required'] = []
        for tm in tag_manifests_obj:
            resp['Tag-Manifests-Required'].append(tm.name)

        resp['Tag-Files-Required'] = []
        for tf in tag_files_obj:
            resp['Tag-Files-Required'].append(tf.name)

        def clean_empty(d):
            if not isinstance(d, (dict, list)):
                return d
            if isinstance(d, list):
                return sorted([v for v in (clean_empty(v) for v in d) if v is not None])
            return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v is not None}

        resp = clean_empty(resp)

        return self.render_to_json_response(resp, **kwargs)

class BagItProfileAPIAdminView(ManagingArchivistMixin, JSONResponseMixin, TemplateView):

    def render_to_response(self, context, **kwargs):
        if not self.request.is_ajax():
            raise Http404
        resp = {'success': 0}

        if 'action' in self.kwargs:
            obj = get_object_or_404(BagItProfile,pk=context['profile_pk'])
            if self.kwargs['action'] == 'delete':
                obj.delete()
                resp['success'] = 1

        return self.render_to_json_response(resp, **kwargs)
